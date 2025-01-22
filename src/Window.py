
from typing import Tuple
import psutil
import win32api, win32gui, win32con, win32process
from src.Globals import _G

class Window:
    def __init__(self, hwnd: int) -> None:
        self._hwnd = hwnd
        self._update_window_info()

    def _update_window_info(self) -> None:
        try:
            rect = win32gui.GetWindowRect(self._hwnd)
            self._window_pos = (rect[0], rect[1])
            self._window_size = (rect[2] - rect[0], rect[3] - rect[1])
        except:
            pass
    
    @property
    def exists(self) -> bool:
        try:
            return win32gui.IsWindow(self._hwnd)
        except:
            return False
    
    @property
    def title(self) -> str:
        try:
            return win32gui.GetWindowText(self._hwnd)
        except:
            return ""
    
    @property
    def visible(self) -> bool:
        try:
            return win32gui.IsWindowVisible(self._hwnd)
        except:
            return False
    
    @property
    def pid(self) -> int | None:
        try:
            _, pid = win32process.GetWindowThreadProcessId(self._hwnd)
            return pid
        except:
            return
    
    @property
    def x(self) -> int:
        self._update_window_info()
        return self._window_pos[0]
    @x.setter
    def x(self, value: int | float) -> None:
        self.move(value, self.y)

    @property
    def y(self) -> int:
        self._update_window_info()
        return self._window_pos[1]
    @y.setter
    def y(self, value: int | float) -> None:
        self.move(self.x, value)
        
    @property
    def width(self) -> int:
        self._update_window_info()
        return self._window_size[0]
    @width.setter
    def width(self, value: int | float) -> None:
        self.size(value, self.height)
    
    @property
    def height(self) -> int:
        self._update_window_info()
        return self._window_size[1]
    @height.setter
    def height(self, value: int | float) -> None:
        self.size(self.width, value)
    
    def set_cpu_affinity(self, core_ids: list | int) -> None:
        try:
            if isinstance(core_ids, int):
                core_ids = [core_ids]
            
            process = psutil.Process(self.pid)
            process.cpu_affinity(core_ids)
        except:
            pass
    
    def focus(self) -> None:
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_RESTORE)
            win32gui.ShowWindow(self._hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(self._hwnd)
        except:
            pass
    
    def minimize(self) -> None:
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_MINIMIZE)
        except:
            pass
        
    def close(self) -> None:
        try:
            win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)
        except:
            pass

    def terminate(self) -> None:
        try:
            process_handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, self.pid)
            win32api.TerminateProcess(process_handle, 0)
            win32api.CloseHandle(process_handle)
        except:
            pass
        
    def move(self, x: int | float, y: int | float) -> None:
        try:
            self._update_window_info()
            if isinstance(x, float):
                x = int(_G.screen_width * x)
            if isinstance(y, float):
                y = int(_G.screen_height * y)

            self._window_pos = (x, y)
            win32gui.SetWindowPos(self._hwnd, win32con.HWND_TOP, x, y, self._window_size[0], self._window_size[1], 0)
        except:
            pass

    def size(self, width: int | float, height: int | float) -> None:
        try:
            self._update_window_info()
            if isinstance(width, float):
                width = int(_G.screen_width * width)
            if isinstance(height, float):
                height = int(_G.screen_height * height)
            
            self._window_size = (width, height)
            win32gui.SetWindowPos(self._hwnd, win32con.HWND_TOP, self.x, self.y, width, height, 0)
        except:
            pass

    def click(self, x: int | float, y: int | float, amount: int = 1) -> None:
        try:
            if _G.paused_usage or _G.paused_usage_by_user:
                return
                
            self._update_window_info()
            if isinstance(x, float):
                x = int(self._window_size[0] * x)
            if isinstance(y, float):
                y = int(self._window_size[1] * y)

            abs_x = self.x + x
            abs_y = self.y + y
        
            for _ in range(amount):
                win32api.SetCursorPos((abs_x, abs_y))
                    
                self.focus()
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        except:
            pass
    
    def get_pixel_col(self, x: int | float, y: int | float) -> Tuple[int, int, int]:
        try:
            self._update_window_info()
            if isinstance(x, float):
                x = int(self._window_size[0] * x)
            if isinstance(y, float):
                y = int(self._window_size[1] * y)

            x = self.x + x + 10
            y = self.y + y + 30
            
            # win32api.SetCursorPos((x, y))

            hdc = win32gui.GetDC(0)
            pixel_color = win32gui.GetPixel(hdc, x, y)
            win32gui.ReleaseDC(0, hdc)

            r = (pixel_color & 0xFF)
            g = (pixel_color >> 8) & 0xFF
            b = (pixel_color >> 16) & 0xFF

            return r, g, b
        except:
            return 0, 0, 0
