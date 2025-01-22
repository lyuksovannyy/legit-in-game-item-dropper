
import asyncio
import random
from datetime import datetime, timedelta
import config
from .Globals import _G
from .Window import Window
from .Sandboxie import Sandboxie
from .Login import get_credentials, get_guard_code
import pyautogui

async def _box_timeout_terminate(box: Sandboxie, data: dict, app: dict, game: Window) -> None:
    date = datetime.now().replace(microsecond=0)
    timeout = date + app.get("play_time", timedelta(seconds=60))
    while timeout > date and not _G.terminated and game and game.exists:
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue

        steam_app = box.get_process_by_title("Steam")
        if steam_app and steam_app.visible:
            steam_app.close()

        date = datetime.now().replace(microsecond=0)
        box.info("Playing in %s for %s" % (app.get("name"), timeout - date))
        await asyncio.sleep(1)
    
    date = datetime.now().replace(microsecond=0)
    close_at = date + timedelta(seconds=15)
    while close_at > date and game and game.exists:
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue
        
        date = datetime.now().replace(microsecond=0)
        game.close()
        box.info("Terminating %s in %s" % (app.get("name"), close_at - date))
        await asyncio.sleep(1)
        
    if game and game.exists:
        game.terminate()
    
    data["cooldown_until"] = int((datetime.now().replace(microsecond=0) + app.get("cooldown", config.COOLDOWN_TIME)).timestamp())
    if app.get("period_launch_limit"):
        if data["launch_count"] == 0:
            data["last_launch_at"] = int((datetime.now().replace(microsecond=0)).timestamp())
            
        data["launch_count"] += 1
    _G.config._save()
        
async def _app_task(box: Sandboxie, app: dict) -> None:
    app_id = app.get("id")
    app_name = app.get("name")
    app_params = app.get("params", "")
    period_launch_limit = app.get("period_launch_limit")
    period_cooldown = app.get("period_cooldown", timedelta(days=1))
    eula = app.get("eula", False)
    callback = app.get("callback")
    run_instances_type = app.get("run_instances_type", "blacklist")
    run_instances_list = app.get("run_instances_list", [])
        
    if (run_instances_type == "whitelist" and box.name not in run_instances_list) or (run_instances_type == "blacklist" and box.name in run_instances_list):
        return
    
    # setting up data
    if box.name not in _G.config:
        _G.config[box.name] = {}
    data = _G.config[box.name]
    if str(app_id) not in data:
        data[str(app_id)] = {}
    data: dict = data[str(app_id)]
    
    for k, v in {
        "cooldown_until": 0,
        "launch_count": 0,
        "last_launch_at": 0
    }.items():
        if k not in data:
            data[k] = v
            
    if data.get("cooldown_until") > datetime.now().timestamp():
        return
    
    if datetime.fromtimestamp(data.get("last_launch_at", 0)) + period_cooldown <= datetime.now():
        data["launch_count"] = 0
    
    _G.config._save()
    
    if period_launch_limit:
        if data.get("launch_count", 0) >= period_launch_limit:
            return
    
    game = None
    steam = None
    window = None
    waiting_until = datetime.now().replace(microsecond=0) + config.ACTION_TIMEOUT
    while not _G.terminated and waiting_until > datetime.now():
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue
            
        srv_err = box.get_process_by_title("Steam Service Error")
        if srv_err:
            box.info("Steam service error")
            srv_err.focus()
            srv_err.click(0.58, 0.78)
            
        window = await box.wait_for(
            [
                "Sign in to Steam",
                "Steam Dialog",
                app_name,
                "Steam",
            ],
            1, False
        )
        await asyncio.sleep(0.2)
        
        if not window:
            box.info("Launching Steam")
            box.start('"' + config.STEAM_EXE_PATH + '" ' + config.STEAM_PARAMS)
            await asyncio.sleep(3)
            continue
    
        if "Sign in to Steam" in window.title:
            logged_in = False
            skip_auto_login = False
            date = datetime.now().replace(microsecond=0)
            login_allowed_until = date + timedelta(minutes=3)
            steam_app = None
            black_screen_counter = 0
            while not logged_in and login_allowed_until > date and not _G.terminated:
                date = datetime.now().replace(microsecond=0)
                if _G.currently_logging_in and _G.currently_logging_in != box.name or _G.paused_usage_by_user:
                    login_allowed_until = date + timedelta(minutes=3)
                    await asyncio.sleep(1)
                    continue
                
                if black_screen_counter >= 10:
                    box.delete()
                    logged_in = True # fake
                    break
                
                _G.currently_logging_in = box.name
                _G.paused_usage = True
                
                box.info("Login into your account", "(%s)" % str(login_allowed_until - date))
                steam_app = await box.wait_for(
                    [
                        "Sign in to Steam",
                        "Steam Service Error", 
                        "Steam"
                    ], 
                    1, False
                )
                await asyncio.sleep(1)
                
                if steam_app:
                    steam_app.focus()
                    
                if not steam_app or (steam_app.width < 705 and steam_app.height < 440):
                    login_allowed_until = date + timedelta(minutes=3)
                    box.info("Not found/too small...")
                    continue
                
                steam_app.move(10, 10)
                steam_app.focus()
                r, g, b = steam_app.get_pixel_col(30, 30)
                if r == 0 and g == 0 and b == 0:
                    login_allowed_until = date + timedelta(minutes=3)
                    black_screen_counter += 1
                    box.info("Black screen...")
                    continue
                
                if "Sign in to Steam" in steam_app.title and config.AUTO_LOGIN_METHOD and not skip_auto_login:
                    no_prefix = box.name.removeprefix(config.SANDBOXIE_BOXES_PREFIX)
                    raw = no_prefix.split("_", 1)
                    number = raw[0].replace("a", "").isnumeric() if "_" in no_prefix else False
                    bot_login = raw[1] if number else box.name
                    login, password = await get_credentials(bot_login)
                    
                    if not login:
                        print("Bot not found in ASF.")
                        skip_auto_login = True
                        continue
                    
                    await asyncio.sleep(3)
                    box.info("Trying to login...")
                    
                    # steam_app.focus()
                    # steam_app.click(222, 141) # login field
                    
                    # await asyncio.sleep(1.5)
                    steam_app.focus()
                    pyautogui.typewrite(login) # type login
                    
                    await asyncio.sleep(0.3)
                    steam_app.focus()
                    # steam_app.click(222, 213) # password field
                    pyautogui.hotkey("tab")
                    
                    await asyncio.sleep(0.3)
                    steam_app.focus()
                    pyautogui.typewrite(password) # type password
                    
                    await asyncio.sleep(0.3)

                    steam_app.focus()
                    # steam_app.click(222, 300) # login button
                    pyautogui.hotkey("tab")
                    pyautogui.hotkey("tab")
                    await asyncio.sleep(0.3)
                    pyautogui.hotkey("enter")
                    
                    guard_code = await get_guard_code(login, password)
                    if guard_code:
                        await asyncio.sleep(5)
                        steam_app.focus()
                        # steam_app.click(352, 188) # guard code button
                        
                        await asyncio.sleep(0.5)
                        steam_app.focus()
                        pyautogui.typewrite(guard_code) # type guard code
                        await asyncio.sleep(1)
                    
                    skip_auto_login = True
                    await asyncio.sleep(1)
                
                if steam_app and "Sign in to Steam" not in steam_app.title:
                    logged_in = True
            
            _G.currently_logging_in = False
            _G.paused_usage = False
            if logged_in:
                continue
            
            break
        
        if app_name in window.title:
            box.info("Game %s is already running..." % app_name)
            game = window
            break
          
        if "Steam Dialog" in window.title: # Cloud out of date error / Cloud conflict
            box.info("Steam out of sync/cloud conflict")
            window.focus()
            window.click(430, 240)
            await asyncio.sleep(0.1)
            window.focus()
            window.click(280, 355)
            await asyncio.sleep(0.1)
            window.focus()
            window.click(280, 325)
            await asyncio.sleep(0.1)
            window.focus()
            window.click(500, 512)
            continue
                    
        if "Steam" in window.title:
            steam = window
            if not window.visible or window.width < 800:
                window.focus()
                # skip if steam in not poped up
                # skip steam updated dialog
                continue

            box.info("Launching", app_name)
            box.start('"' + config.STEAM_EXE_PATH + '" ' + config.STEAM_PARAMS + " " + config.STEAM_GAME_PARAMS.format(id=app_id, params=app_params))
            
            if eula:
                steam.focus()
                steam.size(1010, 600)
                await asyncio.sleep(1.5)
                steam.click(615, 540)
    
    # game = game or await box.wait_for(app_name, 1, False)
    # if not game or not game.exists:
        # box.info("Launching", app_name)
        # box.start('"' + config.STEAM_EXE_PATH + '" ' + config.STEAM_PARAMS + " " + config.STEAM_GAME_PARAMS.format(id=app_id, params=app_params))

        # steam_dialog = await box.wait_for("Steam Dialog", 3)
        # while steam_dialog:
            # steam_dialog = await box.wait_for("Steam Dialog", 3)
            # if not steam_dialog:
                # break
            # 
            # box.info("Steam out of sync/cloud conflict")
            # steam_dialog.focus()
            # steam_dialog.click(280, 355)
            # await asyncio.sleep(0.1)
            # steam_dialog.click(280, 325)
            # await asyncio.sleep(0.1)
            # steam_dialog.click(500, 512)
            
        # await asyncio.sleep(1)
        # steam = await box.wait_for("Steam", 3)
        # if eula and steam:
            # steam.focus()
            # steam.size(1010, 600)
            # await asyncio.sleep(1.5)
            # steam.click(615, 540)

        # game = await box.wait_for(app_name, config.ACTION_TIMEOUT)

    steam = await box.wait_for("Steam", 1)
    if steam:
        steam.close()

    if not game:
        return
    
    core1 = random.randint(0, _G.total_cpu - 1)
    core2 = core2 = random.randint(0, _G.total_cpu - 1)
    while core2 == core1: # reroll
        core2 = random.randint(0, _G.total_cpu - 1)
        
    game.set_cpu_affinity([core1, core2])
    
    tasks = []
    if callback:
        tasks.append(asyncio.Task(callback(game)))
        
    _G.in_grid_apps.append(game)
    tasks.append(asyncio.Task(_box_timeout_terminate(box, data, app, game)))
    await asyncio.gather(*tasks)
                    
async def run_box(box_name: str) -> None:
    app_tasks = []
    
    if "-1" in _G.config.get(box_name, {}):
        del _G.config[box_name]["-1"]

    box = Sandboxie(box_name)

    for app in _G.apps:
        if not config.EXPERIMENTAL_RUN_MULTIPLE_GAMES:
            await _app_task(box, app)
            continue
        
        app_tasks.append(asyncio.Task(_app_task(box, app)))
            
    if config.EXPERIMENTAL_RUN_MULTIPLE_GAMES:
        await asyncio.gather(*app_tasks)
    
    await asyncio.sleep(3)
    box.terminate()

    _G.active_boxes.remove(box_name)
    _G.completed_boxes.append(box_name)
    