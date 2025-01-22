from src import Window
from src.Globals import _G
from datetime import timedelta
import asyncio
import pyautogui

# SETTINGS = {
#     # Drops every 10 minutes (max 5 per day)
#     "id": 3231090,
#     "name": "Amarillo's Butt Slapper",
#     "play_time": timedelta(minutes=6),
#     "cooldown": timedelta(minutes=5), 
#     "period_launch_limit": 5,
#     "period_cooldown": timedelta(hours=24),
# }

SETTINGS = {
    # Drops every 10 minutes (max 5 per day)
    "id": 3231090,
    "name": "Amarillo's Butt Slapper",
    "play_time": timedelta(minutes=55),
    "cooldown": timedelta(hours=23), 
}

async def CALLBACK(game: Window) -> None:
    white_reached = False
    timer_renewed = 0
    
    max_timer_renews = str(9 / SETTINGS.get("period_launch_limit", 1))
    max_timer_renews = int(max_timer_renews.split(".")[0]) if "." in max_timer_renews else int(max_timer_renews)
    
    while game and game.exists:
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue
        
        if timer_renewed >= max_timer_renews:
            game.close()
            break
        
        game.size(256, 256)
        game.focus()
        
        r, g, b = game.get_pixel_col(0.5, 10)
        if (r, g, b) == (28, 0, 38): # somehow came to settings (idk how nahui)
            pyautogui.hotkey("esc")
            await asyncio.sleep(1)
        
        r, g, b = game.get_pixel_col(20, 40)
        if (r, g, b) == (64, 64, 64):
            r, g, b = game.get_pixel_col(192, 208) # progress bar
            if white_reached and r == 96 and g == 96 and b == 96:
                white_reached = False
                timer_renewed += 1
            
            elif not white_reached and r == 255 and g == 255 and b == 255:
                white_reached = True
                
            await asyncio.sleep(1)
            continue
        
        if (game.width, game.height) == (256, 256):
            game.click(128, 165)
            await asyncio.sleep(0.1)
            game.click(20, 40)
                
        await asyncio.sleep(1)