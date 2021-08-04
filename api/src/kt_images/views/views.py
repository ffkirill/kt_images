import json
from os import mkdir
from pathlib import Path
from typing import Union, Optional, List

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r201, r302, r404, r400

import kt_images.model as KtModel
from kt_images.settings import Settings
from kt_images.views.exceptions import HTTPStreamedException


class ModelViewMixin:
    storage: KtModel.Repository
    settings: Settings

    def __init__(self: PydanticView, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = self.request.app.storage
        self.settings = self.request.app.settings

    async def get_image_or_404(self, image_id: int) -> KtModel.Image:
        image: KtModel.Image = await self.storage.get_image(image_id)
        if image is None:
            raise web.HTTPNotFound(reason=f'Image <{image_id}> is not found')
        return image


class ImageCollectionModelView(ModelViewMixin, PydanticView):
    async def get(self, /,
        tag: Optional[str] = None,
        tags_all: Optional[List[str]] = None,
        tags_any: Optional[List[str]] = None) -> r200[List[KtModel.Image]]:
        """
        List Images entities, optionally filter by tags
        Response is streamed due to performance consideration
        See https://github.com/tolgahanuzun/Streaming_API/blob/master/chunked_app.py
        for streamed response details.
        The streamed data is followed by totals object info.
        
        Query params:
          tag: Filter by single tag
          tags_all: Filter by tags subset
          tags_any: Filter by tags set intersection
          If multiple kind of filters appears in query, logical "and" is applied.
        """
        images_chunks = self.storage.list_images(tag, tags_all, tags_any)
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={'Content-Type': 'application/json'},
        )
        response.enable_chunked_encoding()
        await response.prepare(self.request)
        try:  
            # Manually form chunked json
            await response.write(b'[')
            total_chunks = 0
            total_images = 0
            async for chunk in images_chunks:
                await response.write(json.dumps(chunk).encode())
                await response.write(b', ')
                total_chunks += 1
                total_images += len(chunk)
            await response.write(json.dumps({'totalImages': total_images, 'totalChunks': total_chunks}).encode())
            await response.write(b']')
            await response.write_eof()
            return response
        except Exception as exc:
            raise HTTPStreamedException(reason=exc, response=response)

    async def post(self, image: KtModel.Image) -> Union[r201[KtModel.Image], r400[KtModel.Error]]:
        """Create a new image"""
        return web.json_response(
            (await self.storage.add_image(image)).dict(),
            status=201)


class ImageItemModelView(ModelViewMixin, PydanticView):
    async def get(self, image_id: int, /) -> Union[r200[KtModel.Image], r404[KtModel.Error]]:
        """View Image"""
        image = await self.get_image_or_404(image_id)
        return web.json_response(image.dict())


class ImageItemUploadModelView(ModelViewMixin, PydanticView):
    async def post(self, image_id: int, filename: str, /) -> Union[r201[KtModel.Image], r404[KtModel.Error]]:
        """Upload file
        
        TODO: Validate filename, image format
        """
        request = self.request
        reader = await request.multipart()
        image = await self.get_image_or_404(image_id)
        field = await reader.next()
        assert field.name == 'image'
        filename = field.filename
        if filename != image.filename:
            raise web.HTTPBadRequest(reason=f'Invalid filename {filename}')
        # You cannot rely on Content-Length if transfer is chunked.
        size = 0
        upload_path = Path(self.settings.uploads_dir / str(image.image_id))
        if not upload_path.exists():
            mkdir(upload_path)
        with open(self.settings.uploads_dir / str(image.image_id) / filename, 'wb') as f:
            while True:
                chunk = await field.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        return web.Response(text='{} sized of {} successfully stored'
                                ''.format(filename, size))
    
    async def get(self, image_id: int, filename: str, /) -> Union[r302[web.HTTPFound], r404[KtModel.Error]]:
        image = await self.get_image_or_404(image_id)
        if filename != image.filename: # TODO: process multiple attachments
            raise web.HTTPNotFound(f'invalid filename {filename}')
        return web.HTTPFound(f'/media/{image_id}/{image.filename}')
