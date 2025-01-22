import os
from datetime import timedelta

# SETTINGS
PAUSE_KEY = "alt"
ALLOWED_ONE_TIME_INSTANCES = 0 # if 0 gonna place your CPU count divided by 3 (ex.: 20 / 3 = 4)
COOLDOWN_TIME = timedelta(hours=4) # global cooldown for apps
ACTION_TIMEOUT = timedelta(seconds=120) # if something goes wrong and it doesn't fixed (for example must login again), skips box after X seconds
SHUTDOWN_PC_AT_NIGHT = True # Shutdown pc at night when farming is completed (00:00 - 07:59)
LOOPS_BEFORE_SHUTDOWN = 15 # After 5 loops gonna shutdowns PC (if SHUTDOWN_PC_AT_NIGHT is enabled)

STEAM_EXE_PATH = r"C:\FarmGames\AltSteam\steam.exe" # Default Steam location
STEAM_GAMES_LIBRARY_PATH = r"C:\Program Files (x86)\Steam\steamapps" # Default Steam's games library
SANDBOXIE_PATH = r"C:\Program Files\Sandboxie-Plus\Start.exe" # Default Sandboxie path

EXPERIMENTAL_RUN_MULTIPLE_GAMES = False # Try to run all games at once (May be really laggy)

# Disabled / ArchiSteamFarm integration
AUTO_LOGIN_METHOD = "ASF" # None / "ASF" | recommended for easy setup
# To make ASF integration work properly all bots must have 'login;password' alias format or it won't accept it
ASF_REMOTE_SERVER = "http://localhost:1242"
ASF_PASSWORD = "replacewithyourownpassword"

APPS_SETTINGS = {
    2923300: { # Banana
        "run_instances_type": "blacklist", # "whitelist" or "blacklist" | Allowed/Disallowed sandboxie instances to run
        "run_instances_list": [ # list[str] | List of sandboxie instances
            # "DefaultBox",
        ],
    },
    440: { # Team Fortress 2
        "run_instances_type": "whitelist",
        "run_instances_list": [ # allow only premium users
            # "STEAM_0_account1",
            # "STEAM_1_account2",
            # "STEAM_2_account3"
        ],
    },
}

SANDBOXIE_BOXES = [
    # Use "setup-bots.bat" with ASF running to easily setup Sandboxie 
    # with all steam accounts and get list that you will provide here
]

# CHANGE ONLY IF YOU KNOW WHAT YOU DOING
SANDBOXIE_TITLE_FORMAT = "[#] [{box_name}] {title} [#]"
SANDBOXIE_INI_PATH = r"C:\Windows\Sandboxie.ini"
SANDBOXIE_BOXES_PREFIX = "STEAM_"
STEAM_PARAMS = "-nofriendsui -noverifyfiles -no-dwrite -silent -language english -clearbeta -cafeapplaunch"
STEAM_GAME_PARAMS = "-applaunch {id} {params}"
DATA_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "data.json")) # C:\ ... \data.json
