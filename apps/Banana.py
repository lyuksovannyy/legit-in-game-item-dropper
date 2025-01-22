from src import Window
from src.Globals import _G
from datetime import timedelta
import asyncio, random

SETTINGS = {
    "id": 2923300, # int | App id (ex. 440(TF2))
    "name": "Banana", # str | Window title that script search for (ex. "TF2", script gonna search window with title: "[#] <box_name> TF2 [#]")
    # Optional to fill
    "params": "", # str | Steam launch params for the game
    "play_time": timedelta(seconds=60), # timedelta | Playtime for the game, after this time it closes the game (if game won't closed in 15 seconds, it gonna be terminated)
    "eula": True, # boolean | Confirm eula if appears
    "cooldown": timedelta(hours=3), # timedelta | Cooldown before running game again.
    "period_launch_limit": None, # int | How much it can be ran by given period of time, None for no limit
    "period_cooldown": timedelta(days=1), # timedelta | Cooldown before resetting period_launch_limit
}

async def CALLBACK(game: Window) -> None:
    while game and game.exists:
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue
        
        game.size(256, 256)
        game.focus()
        r, g, b = game.get_pixel_col(0.5, 0.1)
        print(r, g, b)
        if (r, g, b) == (35, 31, 32): # unity intro
            await asyncio.sleep(1)
            continue
        
        await asyncio.sleep(5)
            
        for i in range(3):
            game.click(random.uniform(0.49, 0.51), random.uniform(0.6, 0.58))
            await asyncio.sleep(0.5)
        game.close()
