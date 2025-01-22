from src import Window
from src.Globals import _G
from datetime import timedelta
import asyncio

SETTINGS = {
    # 1 drop every day~
    "id": 440,
    "name": "Team Fortress 2 - Direct3D 9 - 64 Bit",
    "params": "-sw -w 640 -h 480 -refresh 25 -nocrashdialog -nosound -nopreload -nojoy -novid -sillygibs +r_rootlod 2 +mat_picmip 2 +mat_reducefillrate 1 +r_waterforceexpensive 0 +r_waterforcereflectentities 0 +r_shadowrendertotexture 0 +mat_colorcorrection 0 +mat_trilinear 0 +mat_hdr_level 0 +volume 0 +max_fps 60",
    "play_time": timedelta(minutes=11),
    "cooldown": timedelta(hours=24),
}

async def CALLBACK(game: Window) -> None:
    claimed = False
    while game and game.exists:
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue
        
        game.focus()
        r, g, b = game.get_pixel_col(494, 34)
        if (r == 211 and g == 126 and b == 27):
            game.click(480, 78)
            await asyncio.sleep(0.1)
            
        r, g, b = game.get_pixel_col(450, 140)
        if (r == 206 and g == 194 and b == 162):
            game.click(480, 173)
            await asyncio.sleep(0.1)
                
        r, g, b = game.get_pixel_col(10, 0.5)
        if (r == 42 and g == 39 and b == 37):
            game.click(480, 465)
            claimed = True
        elif claimed:
            game.terminate()

        await asyncio.sleep(1)