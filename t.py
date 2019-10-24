import asyncio
from hachiko.hachiko import AIOWatchdog

@asyncio.coroutine
def watch_fs():
    watch = AIOWatchdog('/home/ymq/tst')
    watch.start()
    while 1:
        yield from asyncio.sleep(1)
    print('watch stoped .....')
    watch.stop()

asyncio.get_event_loop().run_until_complete(watch_fs())
