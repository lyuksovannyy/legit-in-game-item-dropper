
import os
import subprocess
import asyncio
from datetime import datetime
import config
from .Globals import _G

async def iter_boxes() -> None:
    ran_loops = 0
    _G.queued_boxes = config.SANDBOXIE_BOXES.copy()
    while not _G.terminated:
        try:
            for box_name in _G.active_boxes:
                for k, v in _G.parallel_instances.items():
                    box_already_in_list = False
                    for _k, _v in _G.parallel_instances.items():
                        if box_name == _v:
                            box_already_in_list = True
                            break
                    
                    if not v and not box_already_in_list:
                        _G.parallel_instances[k] = box_name
                        break
                    
            if len(_G.queued_boxes) > 0 and len(_G.active_boxes) < config.ALLOWED_ONE_TIME_INSTANCES:
                box_name = _G.queued_boxes.pop(0)
                _G.active_boxes.append(box_name)

            if len(_G.completed_boxes) == len(config.SANDBOXIE_BOXES):
                hour = datetime.now().hour
                if config.SHUTDOWN_PC_AT_NIGHT and hour >= 0 and hour < 8:
                    print("Shutting down PC after %s loop(s)" % str(int(config.LOOPS_BEFORE_SHUTDOWN) - ran_loops))
                    if ran_loops >= config.LOOPS_BEFORE_SHUTDOWN:
                        subprocess.run(["shutdown", "/s", "/f"])
                        os._exit(0)
                    
                    ran_loops += 1

                print("Sleeping next 60 seconds...")
                await asyncio.sleep(60)
                    
                _G.queued_boxes = config.SANDBOXIE_BOXES.copy()
                _G.active_boxes = []
                _G.completed_boxes = []
                
            await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("Bye!")
            _G.terminated = True
            os._exit(0)
