from typing import TypedDict, Union, Any

from aiohttp.web import Application

from kt_images.db import PgService
from kt_images.settings import Settings


class KtImagesAppMapping(TypedDict):
    db: PgService
    config: Settings
    model: Any  # Workaround

KtImagesApp = Union[Application, KtImagesAppMapping]