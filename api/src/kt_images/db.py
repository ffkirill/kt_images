from typing import Tuple, Any

from aiohttp import web
from aiopg import create_pool


class DbError(Exception):
    pass


class PgService:
    """DB Service. Encapsulates connection pool creation"""
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


async def init_pg(app: web.Application):
    app['db'] = PgService(app['config'].pg_dsn)


async def close_pg(app: web.Application):
    if app['db']._pool:
        app['db']._pool.close()
        await app['db']._pool.wait_closed()
