import asyncio
import time
import tracemalloc
tracemalloc.start()
 
async def getdatafromazure(delay):
    await asyncio.sleep(delay)
    return {'data':'summy data'}

async def getdatafromdb(delay):
    await asyncio.sleep(delay)
    return {'data':'summy data'}

async def main():
    start = time.time()
    result = await asyncio.gather(getdatafromazure(5),getdatafromdb(3))
    end = time.time()
    print(end-start)
    return result

print(asyncio.run(main()))