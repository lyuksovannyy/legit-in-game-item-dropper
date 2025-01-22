
import os
import sys
import importlib
import asyncio
import argparse
import config
from src import _G, iter_boxes, place_in_grid, parallel_workspace, Pause, parse_bots, create_box

src_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
apps_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "apps"))

def prepare_app(dir: str, filename: str) -> None:
    if filename.endswith(".py") and filename != "__init__.py":
        file_path = os.path.join(dir, filename)

        spec = importlib.util.spec_from_file_location(filename[:-3], file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        settings: dict = module.__dict__.get("SETTINGS")
        callback = module.__dict__.get("CALLBACK")
        
        settings["callback"] = callback
        if settings["id"] in config.APPS_SETTINGS:
            settings.update(config.APPS_SETTINGS[settings["id"]])

        if settings:
            print("Loaded:", filename, ("with callback" if settings.get("callback") else ""))
            _G.apps.append(settings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some boolean arguments.")
    parser.add_argument("--setup-bots", type=bool, help="Boolean", default=False)
    args = parser.parse_args()
                
    sys.path.append(os.path.abspath(src_directory))
    
    async def main():
        if args.setup_bots:
            bots = await parse_bots()
            boxes = []
            num = 0
            for login, password in bots:
                num += 1
                prefix = "a" * (len(str(num)) - 1)
                
                box_name = config.SANDBOXIE_BOXES_PREFIX + prefix + str(num) + "_" + login
                boxes.append('"' + box_name + '"')
                create_box(box_name)
            
            print("\n== Insert these into your config file ==\n")
            print(",\n".join(boxes))
            print("\n== Insert these into your config file ==")
            
            return
    
        for variable, path in [
            ("STEAM_GAMES_LIBRARY_PATH", config.STEAM_GAMES_LIBRARY_PATH),
            ("STEAM_EXE_PATH", config.STEAM_EXE_PATH),
            ("SANDBOXIE_PATH", config.SANDBOXIE_PATH),
            ("SANDBOXIE_INI_PATH", config.SANDBOXIE_INI_PATH)
        ]:
            if not os.path.exists(path):
                print("\n!!!", variable + ":", path, "isn't correct, provide valid one. !!!")
                return
                
        for filename in os.listdir(apps_directory):
            prepare_app(apps_directory, filename)
    
        if config.ALLOWED_ONE_TIME_INSTANCES <= 0:
            config.ALLOWED_ONE_TIME_INSTANCES = round(_G.total_cpu / 3)
        
        elif config.ALLOWED_ONE_TIME_INSTANCES > _G.total_cpu:
            print("Invalid CPU count provided.")
            os._exit(-1)
            
        print("PC have %s cores" % _G.total_cpu)
        print("Running %s parallel instances" % (config.ALLOWED_ONE_TIME_INSTANCES if config.ALLOWED_ONE_TIME_INSTANCES < len(config.SANDBOXIE_BOXES) else len(config.SANDBOXIE_BOXES)))
            
        if len(config.SANDBOXIE_BOXES) < 0:
            print("Add at least one box name to start the script.")
            os._exit(-2)

        Pause.start()
    
        await asyncio.gather(iter_boxes(), place_in_grid(), *[asyncio.Task(parallel_workspace(str(num))) for num in range(1, config.ALLOWED_ONE_TIME_INSTANCES + 1) if len(config.SANDBOXIE_BOXES) >= num])
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())