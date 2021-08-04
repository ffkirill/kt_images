import logging
from aiohttp import web

from kt_images.settings import Settings
from kt_images.middleware import process_errors
from kt_images.settings import Settings
from kt_images.application import KtImagesWebApp


def init_app(settings: Settings):
    """Create app, setup dependencies"""
    logging.basicConfig(level=logging.DEBUG)
    app: KtImagesWebApp = KtImagesWebApp(middlewares=[process_errors])
    app.settings = settings
    app.setup_repo()
    app.setup_routes()
    return app


def main(argv):
    """HTTP Service entry point"""
    settings = Settings(argv)
    app = init_app(settings)
    web.run_app(app, host=settings.host, port=settings.port)
