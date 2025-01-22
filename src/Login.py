
try:
    import config
    ASF_REMOTE_SERVER = config.ASF_REMOTE_SERVER
    ASF_PASSWORD = config.ASF_PASSWORD
except:
    ASF_REMOTE_SERVER = "http://192.168.2.1:1242"
    ASF_PASSWORD = "qwe"
    
import asyncio
import aiohttp
from datetime import datetime, timedelta

CACHE_EXPIRE_TIME = timedelta(minutes=10)
CACHED_BOTS, CACHE_EXPIRES_AT = [], datetime.now()

async def asf_command(command: str, remote: str = ASF_REMOTE_SERVER, password: str = ASF_PASSWORD) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                remote + "/Api/Command",
                json={"Command": command}, 
                headers = {
                    "Content-Type": "application/json",
                    "Authentication": password
                }
            ) as response:
                if response.status != 200:
                    print("ASF Error:", response.status, (await response.text()))
                    return
                
                data: dict = await response.json()
                
                if not data.get("Success"):
                    print("ASF Error:", response.status, data.get("Message", "Unknown Error"))
                    return

                return data.get("Result")
    except:
        return None

async def parse_bots() -> list[tuple[str, str]]:
    global CACHE_EXPIRE_TIME, CACHED_BOTS, CACHE_EXPIRES_AT
    if CACHE_EXPIRES_AT < datetime.now():
        CACHED_BOTS = []
        
    if len(CACHED_BOTS) != 0:
        return CACHED_BOTS

    bots = await asf_command("status asf")
    if not bots:
        return []
    
    bot_list = []
    for string in bots.replace("<", "").split("\n"):
        raw = string.split("> ")[0]
        if ";" not in raw:
            continue
        
        slices = raw.split(";")
        bot_list.append((slices[0], slices[1]))
    
    CACHED_BOTS = bot_list
    CACHE_EXPIRES_AT = datetime.now() + CACHE_EXPIRE_TIME
    return bot_list

async def get_credentials(bot_login: str) -> tuple[str, str] | None:
    bots = await parse_bots()
    
    for login, password in bots:
        if bot_login == login:
            return login, password
    
    return None, None
    
async def get_guard_code(login: str, password: str = None) -> str | None:
    if not password:
        login, password = await get_credentials(login)
        
    if not login:
        print("2FA: Bot not found.")
        return None
    
    result = await asf_command("2fa " + login + ";" + password)
    if not ": " in str(result):
        print("2FA: not configured.")
        return None
    
    code = result.split(": ")[1]
    if len(code) > 5:
        print("2FA: code unavailable.")
        return None
    
    return code

if __name__ == "__main__": # tests
    async def main():
        while True:
            login, password = await get_credentials(input("Bot login: "))
            if not login:
                print("Bot not found or alias is not properly configured.")
                continue
            
            print("Bot: " + login, "with password:", "*"*len(password))
            guard_code = await get_guard_code(login)
            
            if not guard_code:
                print("Bot don't have 2FA configured.")
                break
                
            print("Guard code:", guard_code)
            break
    
    loop = asyncio.get_event_loop()
    output = loop.run_until_complete(main())