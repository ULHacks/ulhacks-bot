"""Provides an abstract interface for a key-value storage"""

class Store:
    async def set(self, key: str, value: str) -> None:
        raise NotImplementedError
    async def get(self, key: str) -> str:
        raise NotImplementedError

def setup(bot) -> None:
    raise NotImplementedError
