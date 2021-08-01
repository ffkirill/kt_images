from typing import List, Optional, Union

from pydantic import BaseModel

from kt_images.settings import Settings
from kt_images.typing import KtImagesApp

class Image(BaseModel):
    """Image entity dataclass"""
    image_id: int = None
    filename: str
    tags: List[str] = []


class Model:
    """Images entities model"""
    app: KtImagesApp = None

    def __init__(self, app):
        self.app = app

    async def add_image(self, image: Image) -> Image:
        pool = await self.app['db'].connection_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    'insert into images (filename, tags) values (%s, %s) returning image_id, filename, tags;',
                    (image.filename, image.tags))
                res_dict = self.app['db'].make_dict(
                    await cur.fetchone(),
                    cur.description)
                return Image(**res_dict)

    async def get_image(self, image_id: int) -> Optional[Image]:
        pool = await self.app['db'].connection_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    'select image_id, filename, tags from images where image_id = (%s)',
                    (image_id, ))
                res = await cur.fetchone()
                if res is None:
                    return
                res_dict = self.app['db'].make_dict(
                    res,
                    cur.description)
                return Image(**res_dict)

    async def list_images(self, tags: Optional[Union[List[int], int]] = None):
        """Generator that yields chunked images list as list of tuple"""
        pool = await self.app['db'].connection_pool()
        make_dict = self.app['db'].make_dict
        config: Settings = self.app['config']
        sql_query = "select image_id, filename, tags from images"
        params = None
        if tags is not None:
            if isinstance(tags, int):
                tags = [tags]
            sql_query += " where tags::int[] @> (%s)"
            params = (tags, )
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                cur.arraysize = config.postgres_arraysize
                await cur.execute(sql_query, params)
                while True:
                    chunk = await cur.fetchmany()
                    if chunk:
                        yield [make_dict(res, cur.description) for res in chunk]
                    else:
                        break
