import json
from typing import Union, Optional, List, Any

from aiohttp import web
from aiohttp.web_exceptions import HTTPException, HTTPServerError
from aiohttp.web_response import StreamResponse
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r201, r204, r404


from kt_images.model import Image


class HTTPStreamedException(Exception):
    """Exception class to pass exception from stream response generator"""
    response: StreamResponse
    reason: Exception

    def __init__(self, reason: Exception, response: StreamResponse):
        self.response = response
        self.reason = reason
        super().__init__(reason)


class ImageCollectionView(PydanticView):
    async def get(self, tags: Optional[str] = None) -> r200[List[Image]]:
        """
        List Images entities, optionally filter by tags
        See https://github.com/tolgahanuzun/Streaming_API/blob/master/chunked_app.py
        for streamed response details.
        The streamed data is followed by totals object info.
        """
        images_chunks = self.request.app['model'].list_images(tags)
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
            async for chunk in images_chunks:
                await response.write(json.dumps([image for image in chunk]).encode())
                await response.write(b', ')
                total_chunks += 1
            await response.write(json.dumps({'totalChunks': total_chunks}).encode())
            await response.write(b']')
            await response.write_eof()
            return response
        except Exception as exc:
            raise HTTPStreamedException(reason=exc, response=response)

    async def post(self, image: Image) -> r201[Image]:
        """Create a new image"""
        return web.json_response(
            await self.request.app['model'].add_image(image))



class ImageItemView(PydanticView):
    async def get(self, image_id: int, /) -> Union[r200[Image], r404[web.HTTPNotFound]]:
        """View Image"""
        res: Image = await self.request.app['model'].get_image(image_id)
        if res is None:
            raise web.HTTPNotFound(reason=f'Image <{image_id}> is not found')
        return web.json_response(res.dict())
