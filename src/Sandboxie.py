from .Window import Window
import win32gui
from datetime import datetime, timedelta
import asyncio
import config
import subprocess
import ctypes, sys

def _append_content_to_sandboxie(content: str) -> None:
    try:
        with open(config.SANDBOXIE_INI_PATH, "a", encoding="utf-8") as file:
            file.write(content)
    except PermissionError:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        with open(config.SANDBOXIE_INI_PATH, "a", encoding="utf-8") as file:
            file.write(content)
        
def _overwrite_content_to_sandboxie(content: str) -> None:
    try:
        with open(config.SANDBOXIE_INI_PATH, "w", encoding="utf-8") as file:
            file.write(content)
    except PermissionError:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        with open(config.SANDBOXIE_INI_PATH, "w", encoding="utf-8") as file:
            file.write(content)

def _sandboxie_content():
    try:
        with open(config.SANDBOXIE_INI_PATH, "r", encoding="utf-8") as file:
            return file.read()
    except PermissionError:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        with open(config.SANDBOXIE_INI_PATH, "r", encoding="utf-8") as file:
            return file.read()

def _prepare_template(sandboxie_ini: str = None) -> None:
    if "Template_Local_SteamIdler" in sandboxie_ini:
        return sandboxie_ini
    
    sandboxie_ini += (
f'''
[Template_Local_SteamIdler]
Tmpl.Title=SteamIdler
Tmpl.Class=Local
BoxNameTitle=y
OpenPipePath={str(config.STEAM_GAMES_LIBRARY_PATH + "*")}
OpenPipePath={str(config.STEAM_EXE_PATH.removesuffix("steam.exe") + "steamapps*")}
NormalFilePath=*\\BepInEx\\*
FakeAdminRights=y
BorderColor=#000000,on,1
'''
    )
    return sandboxie_ini

def _prepare_grouping(group_name: str = "Steam") -> str:
    sandboxie_ini = _sandboxie_content()
        
    raw_users = sandboxie_ini.split("[UserSettings_")
    raw_users.pop(0)
    
    users = [
        (user.split("]", maxsplit=1)[0], user.split("\n\n", maxsplit=1)[0].split("]\n")[1])
        for user in raw_users
    ]

    groups_created = {}
    for user, props in users:
        groups_created[user] = False
        for prop in props.split("\n"):
            if prop.startswith("BoxGrouping=%s:" % group_name):
                groups_created[user] = True
                break
            
    for user, created in groups_created.items():
        if created:
            continue
        
        for _user, props in users:
            if user != _user:
                continue
            
            sandboxie_ini = sandboxie_ini.replace(user + "]\n" + props, user + "]\n" + props + ("\nBoxGrouping=%s:" % group_name))
    
    # _overwrite_content_to_sandboxie(sandboxie_ini)
    return sandboxie_ini

def _append_to_group(needed_box_name: str, needed_group_name: str = "Steam", sandboxie_ini: str = None) -> None:
    groups = {} # user: [group_name: [boxes]]
    
    raw_users = sandboxie_ini.split("[UserSettings_")
    raw_users.pop(0)
    
    users = [
        (user.split("]", maxsplit=1)[0], user.split("\n\n", maxsplit=1)[0].split("]\n")[1])
        for user in raw_users
    ]
    
    for user, props in users:
        for prop in props.split("\n"):
            if not prop.startswith("BoxGrouping="):
                continue
            
            data = prop.removeprefix("BoxGrouping=").split(":", maxsplit=1)
            group_name = data[0]
            boxes = data[1].split("\n", maxsplit=1)[0]
            
            if user not in groups:
                groups[user] = {}
            
            groups[user][group_name] = boxes.split(",")
            sandboxie_ini = sandboxie_ini.replace("BoxGrouping=" + group_name + ":" + boxes, "BoxGrouping=" + group_name + ":")
    
    for user, groups in groups.items():
        filtered_boxes = [] # boxes for 'Steam' group
        for group_name, boxes in groups.items():
            return_boxes = []
            for box in boxes:
                if box.strip() == "":
                    continue
                
                if box == needed_box_name:
                    filtered_boxes.append(box)
                    continue
                
                return_boxes.append(box)

            if group_name == needed_group_name:
                return_boxes.extend(filtered_boxes)
                sandboxie_ini = sandboxie_ini.replace("BoxGrouping=" + group_name + ":", "BoxGrouping=" + group_name + ":" + ",".join(return_boxes))
                continue
            
            sandboxie_ini = sandboxie_ini.replace("BoxGrouping=" + group_name + ":", "BoxGrouping=" + group_name + ":" + ",".join(return_boxes))

    # _overwrite_content_to_sandboxie(sandboxie_ini)
    return sandboxie_ini
        
def create_box(box_name: str, group: str = "Steam") -> None:
    sandboxie_ini = _prepare_grouping(group)
    sandboxie_ini = _prepare_template(sandboxie_ini)

    if box_name not in sandboxie_ini:
        sandboxie_ini += (
f'''
[{box_name}]
Enabled=y
BlockNetworkFiles=y
BorderColor=#000000,on,1
Template=Local_SteamIdler
ConfigLevel=10
BoxNameTitle=y
'''
        )
        
    found_any = False
    groups = sandboxie_ini.split("BoxGrouping")
    for group_boxes in groups:
        boxes = group_boxes.split("=")[1].split("\n")[0]
        if box_name in boxes:
            found_any = True
            break
    
    if not found_any:
        sandboxie_ini = sandboxie_ini.replace("BoxGrouping=:", "BoxGrouping=:" + box_name + ",")
        
    sandboxie_ini = _append_to_group(box_name, group, sandboxie_ini)
    
    _overwrite_content_to_sandboxie(sandboxie_ini)

class Sandboxie:
    def __init__(self, box_name: str) -> None:
        self.name = box_name
    
    def start(self, command: str) -> None:
        subprocess.Popen(
            '"' + config.SANDBOXIE_PATH + '" /box:%s /silent %s' % (self.name, command)
        )
        
    def delete(self) -> None:
        self.terminate()
        subprocess.Popen(
            '"' + config.SANDBOXIE_PATH + '" /box:%s delete_sandbox_silent' % self.name
        )
    
    def terminate(self) -> None:
        subprocess.Popen(
            '"' + config.SANDBOXIE_PATH + '" /box:%s /terminate' % self.name
        )
    
    def info(self, *messages) -> None:
        print("[%s]" % self.name, *messages)
    
    def get_process_by_title(self, title: str, filter_box: bool = True) -> Window | None:
        '''Gathers all windows with given title inside box'''
        if filter_box:
            title = config.SANDBOXIE_TITLE_FORMAT.format(box_name=self.name, title=title)
        hwnds = []
        
        def callback(hwnd: int, hwnds: list):
            try:
                if win32gui.GetWindowText(hwnd) == title:
                    hwnds.append(hwnd)
            except:
                pass
        
        win32gui.EnumWindows(callback, hwnds)
        windows = [Window(hwnd) for hwnd in hwnds]
        
        return Window(hwnds[0]) if len(windows) != 0 else None
    
    async def wait_for(self, titles: str | list[str], timeout_time: timedelta | int = config.ACTION_TIMEOUT, print_text: bool = True) -> Window | None:
        '''Returns None on Timeout (ACTION_TIMEOUT)'''
        if isinstance(timeout_time, int):
            timeout_time = timedelta(seconds=timeout_time)
        
        date = datetime.now().replace(microsecond=0)
        timeout = date + timeout_time
        hwnd = None
        titles = [titles] if isinstance(titles, str) else titles
        while timeout > date and not hwnd:
            for title in titles:
                date = datetime.now().replace(microsecond=0)
                hwnd = self.get_process_by_title(title)
                if hwnd:
                    return hwnd
                
            if print_text:
                print("[%s] Waiting for:" % self.name, timeout - date, "-", " || ".join(titles))
                
            await asyncio.sleep(0.2)
            
        return None
    