import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from . import config as settings


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        api_key_header = os.getenv("API_KEY_HEADER", settings.API_KEY_HEADER)
        expected_api_key = os.getenv("API_KEY", settings.API_KEY)
        api_key = request.headers.get(api_key_header)

        if api_key is None:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Missing API key"},
            )

        if api_key != expected_api_key:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "message": "Invalid API key"},
            )

        response = await call_next(request)
        return response
