from typing import AsyncIterable, List, Optional

from pydantic import BaseModel
from kt_images.db import PgDataBaseConnector

from kt_images.settings import Settings


class Error(BaseModel):
    """Error message `{"error": "reason"}`"""
    error: str


class Image(BaseModel):
    """Image entity dataclass"""
    image_id: int = None
    filename: str
    tags: List[str] = []


class ImageUpload(BaseModel):
    filename: str
    file: None


class Repository:
    """
    Model instances repository
    """
    _connector: PgDataBaseConnector = None
    config: Settings = None

    def __init__(self, connector: PgDataBaseConnector, config: Settings):
        self._connector = connector
        self.config = config

    async def add_image(self, image: Image) -> Image:
        """
        Saves image instance to repo
        """
        pool = await self._connector.connection_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    'insert into images (filename, tags) values (%s, %s) returning image_id, filename, tags;',
                    (image.filename, image.tags))
                res_dict = self._connector.make_dict(
                    await cur.fetchone(),
                    cur.description)
                return Image(**res_dict)

    async def get_image(self, image_id: int) -> Optional[Image]:
        """
        Returns image instance from repo
        """
        pool = await self._connector.connection_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    'select image_id, filename, tags from images where image_id = (%s)',
                    (image_id, ))
                res = await cur.fetchone()
                if res is None:
                    return
                res_dict = self._connector.make_dict(
                    res,
                    cur.description)
                return Image(**res_dict)

    
    async def list_images(self, tag: Optional[str] = None,
        tags_all: Optional[List[str]] = None, 
        tags_any: Optional[List[str]] = None) -> AsyncIterable[List[List[dict]]]:
        """
        Generator that yields chunked images list as list of dict
        """
        pool = await self._connector.connection_pool()
        make_dict = self._connector.make_dict
        sql_query = 'select image_id, filename, tags from images'
        # Single tag is concatenated into tags_all list
        if tag is not None:
            if tags_all is None:
                tags_all = []
            tags_all.append(tag)
        # Process query params values
        params: List[str] = []
        sql_cond = []
        if tags_all is not None:
            sql_cond.append("(tags @> array[%s]::text[])")
            params.append(tags_all)
        if tags_any is not None:
            sql_cond.append("(tags && array[%s]::text[])")
            params.append(tags_any)
        # Concatenate query condition
        if sql_cond:
            sql_query += ' where '
            sql_query += ' and '.join(sql_cond)
        # Fetch data
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                cur.arraysize = self.config.pg_arraysize
                await cur.execute(sql_query, params)
                while True:
                    chunk = await cur.fetchmany()
                    if chunk:
                        # Yield chunk as list of dict
                        yield [make_dict(res, cur.description) for res in chunk]
                    else:
                        break
