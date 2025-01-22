import keyboard
from .Globals import _G
import config

def _on_shift_press(event: keyboard.KeyboardEvent) -> None:
    if event and event.name and config.PAUSE_KEY in event.name.lower():
        _G.paused_usage_by_user = not _G.paused_usage_by_user
        print("Paused:", _G.paused_usage_by_user)

def start():
    keyboard.on_press(_on_shift_press)
    
def stop():
    keyboard.remove_all_hotkeys()