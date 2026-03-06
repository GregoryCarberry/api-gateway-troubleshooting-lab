import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

RATE_LIMIT = 3
WINDOW_SECONDS = 60

client_requests = {}


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in client_requests:
            client_requests[client_ip] = []

        client_requests[client_ip] = [
            timestamp
            for timestamp in client_requests[client_ip]
            if current_time - timestamp < WINDOW_SECONDS
        ]

        if len(client_requests[client_ip]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded"
                }
            )

        client_requests[client_ip].append(current_time)

        response = await call_next(request)
        return response