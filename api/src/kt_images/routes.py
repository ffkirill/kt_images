from aiohttp.web import Application

from kt_images.views import ImageCollectionView, ImageItemView


def setup_routes(app: Application):
    """Setup application routes"""
    app.router.add_view('/images', ImageCollectionView)
    app.router.add_view('/images/{image_id}', ImageItemView)
