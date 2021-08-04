from aiohttp import web
from kt_images.views.exceptions import HTTPStreamedException
from sys import exc_info

@web.middleware
async def process_errors(request: web.Request, handler):
    """Catch exceptions and represent them as json resposes with
    apropriate http statuses.
    Do not use in production, sensetive data in exceptions can leak."""
    try:
        return await handler(request)
    except HTTPStreamedException as exc:
        # Try to cleanup ;
        request.app.logger.error(exc)
        request.app.logger.error(*exc_info())
        await exc.response.write(str(exc.reason).encode())
        await exc.response.write_eof()
    except web.HTTPException as exc:
        request.app.logger.error(exc)
        request.app.logger.error(*exc_info())
        return web.json_response({"error": str(exc)}, status=exc.status)
    except Exception as exc:
        request.app.logger.error(exc)
        request.app.logger.error(*exc_info())
        return web.json_response({"error": str(exc)}, status=500)
