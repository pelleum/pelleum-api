import uvloop
import asyncio

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

loop = None


async def get_event_loop():
    global loop
    if loop is None:
        loop = asyncio.get_event_loop()

    return loop
