"""Provides a JSON file backed key-value storage"""

import json
import asyncio
import os

from . import Store

class JsonStore(Store):
    """This class uses a JSON encoded file

    The file is read on each .get call and rewritten on each .set call.

    """
    DEFAULT_FILENAME = "json-store.json"

    def __init__(self, filename=None):
        if filename is None:
            filename = type(self).DEFAULT_FILENAME
        self.filename = filename
        self.lock = None

    async def set(self, key, value):
        if self.lock is None:
            self.lock = asyncio.Lock()
        async with self.lock:
            await asyncio.to_thread(self._set, key, value)

    def _set(self, key, value):
        # Get data from the file if it exists
        try:
            with open(self.filename) as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        # Don't store empty string values
        key, value = str(key), str(value)
        if not value:
            data.pop(key, None)
        else:
            data[key] = value
        # Write to a temporary file before atomically replacing the actual file
        temp_filename = self.filename + ".tmp"
        with open(temp_filename, mode="w") as file:
            json.dump(data, file, separators=",:")
        os.replace(temp_filename, self.filename)

    async def get(self, key):
        if self.lock is None:
            self.lock = asyncio.Lock()
        async with self.lock:
            return await asyncio.to_thread(self._get, key)

    def _get(self, key):
        with open(self.filename) as file:
            data = json.load(file)
        # Keys that don't exist are ""
        return data.get(str(key), "")

    async def keys(self):
        if self.lock is None:
            self.lock = asyncio.Lock()
        async with self.lock:
            keys = await asyncio.to_thread(self._keys)
        for key in keys:
            yield key

    def _keys(self):
        with open(self.filename) as file:
            data = json.load(file)
        return data.keys()

def setup(bot):
    filename = os.environ.get("ULHACKS_JSON_STORE_FILENAME", None)
    bot.store = JsonStore(filename=filename)
