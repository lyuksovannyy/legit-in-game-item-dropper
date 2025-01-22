import os
import ctypes
from .Config import Config
import config

class _G:
    paused_usage = False
    paused_usage_by_user = False
    currently_logging_in = False # or username
    terminated = False
    in_grid_apps: list = []
    total_cpu = os.cpu_count()
    parallel_instances = {}
    config = Config(config.DATA_FILE_PATH)
    
    apps = []
    queued_boxes = []
    active_boxes = []
    completed_boxes = []
    
    @property
    def screen_width(self):
        return ctypes.windll.user32.GetSystemMetrics(0)
    
    @property
    def screen_height(self):
        return ctypes.windll.user32.GetSystemMetrics(1)

_G = _G()