from aiohttp import web
from kt_images.views import HTTPStreamedException

@web.middleware
async def process_errors(request: web.Request, handler):
    """Catch exceptions and represent them as json resposes with
    aporopriate http statuses.
    Do not use in production, sensetive data in exceptions can leak."""
    try:
        return await handler(request)
    except HTTPStreamedException as exc:
        # Try to cleanup ;
        request.app.logger.error(exc)
        await exc.response.write(str(exc.reason).encode())
        await exc.response.write_eof()
    except web.HTTPException as exc:
        request.app.logger.error(exc)
        return web.json_response({"error": str(exc)}, status=exc.status)
    except Exception as exc:
        request.app.logger.error(exc)
        return web.json_response({"error": str(exc)}, status=500)
