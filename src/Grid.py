
import asyncio
from .Globals import _G

async def place_in_grid() -> None:
    '''Works not really good btw'''
    while not _G.terminated:
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue
        
        last_grid_app = {}
        for window in _G.in_grid_apps:
            if not window or not window.exists:
                _G.in_grid_apps.remove(window)
                continue
            
            x = last_grid_app.get("x", 0) + last_grid_app.get("w", 0)
            y = last_grid_app.get("y", 0) + last_grid_app.get("h", 0)

            y = y if _G.screen_height > y and _G.screen_width <= x else 0
            x = x if _G.screen_width > x else 0
            
            last_grid_app = {
                "x": x,
                "y": y,
                "w": window.width,
                "h": window.height
            }
            
            window.x = last_grid_app["x"]
            window.y = last_grid_app["y"]
            window.width = last_grid_app["w"]
            window.height = last_grid_app["h"]

        await asyncio.sleep(1)
    