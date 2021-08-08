"""Provides a wrapper around two stores being moved"""

import asyncio
from . import Store

class MoveStore(Store):
    """This class wraps two other stores

    Before moving, all data will use the first store.

    When .move() is first awaited, it will start copying all data from the
    first store into the second store using the .keys() async iterator.

    Reading and writing will still work during moving. Unless a key has been
    modified, the first store will be used. When setting a key, the second
    store will be used, and future reads will use the second store.

    What this means is that a call to .move() will stop all writes to the first
    store.

    When it is still moving data, calls to .move() will block until all data
    has been moved.

    After moving, all data will use the second store.

    Future calls to .move() will do nothing.

    """
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.moving = False
        self.moved = False
        self._finished_moving_event = None
        self.modified = set()

    async def move():
        # After move
        if self.moved:
            return False
        # During move
        if self.moving:
            await self._finished_moving_event.wait()
            return True
        # Before move
        self.moving = True
        self._finished_moving_event = asyncio.Event()
        async for key in self.first.keys():
            if key in self.modified:
                continue
            value = await self.first.get(key)
            # This condition is duplicated in case the key was modified during
            # our .get call.
            if key in self.modified:
                continue
            # There's an edge case where a .set is issued before this is called
            # and finishes before we do. The key could will be overwritten with
            # the old value. We simply hope that the use is OK with that.
            await self.second.set(key, value)
        self.moved = True
        self.moving = False
        self.modified = set()
        self._finished_moving_event.set()
        return True

    async def set(self, key, value):
        # After move
        if self.moved:
            return await self.second.set(key, value)
        # Before move
        if not self.moving:
            return await self.first.set(key, value)
        # During move
        value = await self.second.set(key, value)
        self.modified.add(str(key))
        return value

    async def get(self, key):
        # After move
        if self.moved:
            return await self.second.get(key)
        # Before move
        if not self.moving:
            return await self.first.get(key)
        # During move
        if str(key) in self.modified:
            return await self.second.get(key)
        else:
            return await self.first.get(key)

    async def keys(self):
        # After move
        if self.moved:
            async for key in self.second.keys():
                yield key
            return
        # Before move
        if not self.moving:
            async for key in self.first.keys():
                yield key
            return
        # During move
        async for key in self.first.keys():
            yield key
        async for key in self.second.keys():
            yield key
