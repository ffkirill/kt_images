from typing import Tuple, Any

from aiopg import create_pool


class DbError(Exception):
    pass


class PgDataBaseConnector:
    """DB Connector. Encapsulates connection pool creation"""
    _pool = None
    dsn: str = None

    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool = None

    def make_dict(self, raw: Tuple[Any], description):
        """Utility function which makes dict from result tuple"""
        return {k: v for k, v in zip((field.name for field in description), raw)}

    async def connection_pool(self):
        if self._pool is None:
            self._pool = await create_pool(self.dsn)
        return self._pool

    async def release_storage(self, app):
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
