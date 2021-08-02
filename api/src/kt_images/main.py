import logging
from aiohttp import web

from kt_images.db import init_pg, close_pg

from kt_images.routes import setup_routes
from kt_images.model import Model
from kt_images.settings import Settings
from kt_images.middleware import process_errors
from kt_images.typing import KtImagesApp
from kt_images.settings import Settings


async def init_app(config: Settings):
    logging.basicConfig(level=logging.DEBUG)
    app: KtImagesApp = web.Application(middlewares=[process_errors])
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)
    app['config'] = config
    app['model'] = Model(app)
    setup_routes(app)
    return app


def main(argv):
    config = Settings(argv)
    app = init_app(config)
    web.run_app(app, host=config.host, port=config.port)
