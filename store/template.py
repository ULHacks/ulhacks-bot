"""Provides an abstract interface for a key-value storage"""

from collections.abc import AsyncIterator

class Store:
    async def set(self, key: str, value: str) -> None:
        raise NotImplementedError
    async def get(self, key: str) -> str:
        raise NotImplementedError
    # Used to move data between stores. Can be slow / inefficient
    async def keys(self) -> AsyncIterator[str]:
        raise NotImplementedError
