"""Provides a wrapper around two stores being moved"""

import asyncio
from . import Store

class MoveStore(Store):
    """This class wraps two other stores

    Before moving, all data will use the first store.

    When .move() is first awaited, it will start copying all data from the
    first store into the second store using the .keys() async iterator.

    Reading and writing will still work during moving. When getting a key,
    the first store will be used. When setting a key, both stores
    will be used. Calls to .move() will block until all data has been moved and
    return True.

    After moving, all data will use the second store. Calls to .move()
    will do nothing and return False.

    """
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.moving = False
        self.moved = False
        self._finished_moving_event = None

    async def move(self):
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
            value = await self.first.get(key)
            # There's an edge case where a .set is issued before this .get and
            # finishes before the .set. The key could will be overwritten with
            # the old value. We simply hope that the use is OK with that.
            await self.second.set(key, value)
        self.moved = True
        self.moving = False
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
        await self.first.set(key, value)
        await self.second.set(key, value)

    async def get(self, key):
        # After move
        if self.moved:
            return await self.second.get(key)
        # Before or during move
        else:
            return await self.first.get(key)

    async def keys(self):
        # After move
        if self.moved:
            async for key in self.second.keys():
                yield key
            return
        # Before or during move
        else:
            async for key in self.first.keys():
                yield key
