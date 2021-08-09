"""Provides a JSON file backed key-value storage"""

import asyncpg
import os

from . import Store

class PostgresqlStore(Store):
    """This class uses a JSON encoded file

    The file is read on each .get call and rewritten on each .set call.

    """
    DEFAULT_ADDRESS = "postgresql://postgres@localhost/"

    def __init__(self, address=None):
        if address is None:
            address = type(self).DEFAULT_ADDRESS
        self.address = address

    async def set(self, key, value):
        conn = await asyncpg.connect(self.address)
        try:
            async with conn.transaction():
                # Ensure the table exists
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS store (
                        key TEXT NOT NULL PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                ''')
            async with conn.transaction():
                # Don't store empty string values
                key, value = str(key), str(value)
                if not value:
                    await conn.execute('''
                        DELETE FROM store
                        WHERE key = $1;
                    ''', key)
                else:
                    await conn.execute('''
                        INSERT INTO store (key, value)
                        VALUES ($1, $2)
                        ON CONFLICT (key) DO UPDATE
                        SET value = $2;
                    ''', key, value)
        finally:
            await conn.close()

    async def get(self, key):
        conn = await asyncpg.connect(self.address)
        try:
            value = await conn.fetchval('''
                SELECT value FROM store
                WHERE key = $1 LIMIT 1;
            ''', str(key))
            # Keys that don't exist are ""
            return value or ""
        except asyncpg.UndefinedTableError:
            return ""
        finally:
            await conn.close()

    async def keys(self):
        conn = await asyncpg.connect(self.address)
        try:
            async with conn.transaction():
                async for record in conn.cursor('''
                    SELECT key FROM store;
                '''):
                    yield record[0]
        finally:
            await conn.close()
