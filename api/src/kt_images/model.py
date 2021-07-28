from typing import Generator, List, Optional, Tuple, Any

from pydantic import BaseModel


class Image(BaseModel):
    """Image entity dataclass"""
    image_id: int = None
    filename: str
    tags: List[str] = []


class Model:
    """Images entities model"""
    app = None

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

    async def list_images(self, tags: Optional[str] = None):# -> Generator[List[Tuple]]:
        """Generator that yields chunked images list as list of tuple"""
        pool = await self.app['db'].connection_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select image_id, filename, tags from images")
                while True:
                    res = await cur.fetchmany()
                    if res:
                        yield res
                    else:
                        break
