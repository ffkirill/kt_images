from aiohttp import web
from kt_images.db import PgDataBaseConnector
from kt_images.model import Repository
from kt_images.settings import Settings
from kt_images.views import views


class KtImagesWebApp(web.Application):
    settings: Settings
    storage: Repository

    def setup_repo(self):
        """Setup storage"""
        self.storage = Repository(
            PgDataBaseConnector(self.settings.pg_dsn),
            self.settings)
        self.on_cleanup.append(
            self.storage._connector.release_storage)

    def setup_routes(self):
        """Setup application routes"""
        self.router.add_view('/images', views.ImageCollectionModelView)
        self.router.add_view('/images/{image_id}', views.ImageItemModelView)
        self.router.add_view('/images/{image_id}/attachment/{filename}', views.ImageItemUploadModelView)
        self.router.add_static('/media', self.settings.uploads_dir)
