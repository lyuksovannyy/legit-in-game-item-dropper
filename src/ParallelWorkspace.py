import asyncio
from .Globals import _G
from .RunBox import run_box

async def parallel_workspace(id: str) -> None:
    _G.parallel_instances[id] = None
    
    print("Parallel %s started" % id)
    while not _G.terminated:
        if _G.paused_usage or _G.paused_usage_by_user:
            await asyncio.sleep(1)
            continue
        
        box_name = _G.parallel_instances.get(id)
        if not box_name:
            await asyncio.sleep(1)
            continue
        
        await run_box(box_name)
        _G.parallel_instances[id] = None
