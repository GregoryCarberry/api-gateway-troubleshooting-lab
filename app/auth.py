from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .config import API_KEY, API_KEY_HEADER


class APIKeyMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # allow health endpoint without auth
        if request.url.path == "/health":
            return await call_next(request)

        api_key = request.headers.get(API_KEY_HEADER)

        if api_key is None:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Missing API key"}
            )

        if api_key != API_KEY:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "message": "Invalid API key"}
            )

        response = await call_next(request)
        return response