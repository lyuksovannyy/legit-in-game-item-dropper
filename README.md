# legit-in-game-item-dropper
An stupidly slow method to farm ingame daily rewards like in TF2, ABS, Banana with ability to idle multiple instances at the same time

# Prerequirements
- Python 3.11 and added to PATH
- Sandboxie Plus
- ArchiSteamFarm
- Download this project

# Setup
- Run `install.bat`
- Install Second Steam into another (ex.: `C:\legit-in-game-item-dropper\SteamAlt`)
- After installation goto `config.py` and change steam path to second's steam path (You doing this to avoid possible problems with your main steam client, in most cases you'll face issue where you'll need to relogin into your account.)
- Install `ArchiSteamFarm` make configure IPC password and add your accounts to it (aswell Steam Guards), your accounts must have alias in ASF in following format: `login;password` so this script can easily access login, password, steam guard.
- In `config.py` setup access to ASF instance.
- Now you can easily run `setup-bots.bat`, after script is done, you'll get list of your accounts like this:
  `"STEAM_1_account1",`
  `"STEAM_2_account2",`
  `"STEAM_3_account3"`
  `...`
  and paste it to `SANDBOXIE_BOXES` inside `config.py`
- Delete unneeded `scripts` from `apps` folder if you won't to farm some games that listed in.
- You may need to adjust settings in `config.py` for your own (like for TF2, add account names (`STEAM_0_example`) to its whitelist so it have permit to idle in this game, or other settings)
- After all those steps you can easily run `start.bat`

# For developers
If you would like to make script for your own game to idle,
reffer to `apps/Banana.py` it have all instructions described how to
make your own one script.
