import os

import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from . import config as settings

# Allow environment overrides before importing modules that read config constants.
settings.API_KEY = os.getenv("API_KEY", settings.API_KEY)
settings.BACKEND_BASE_URL = os.getenv("BACKEND_URL", settings.BACKEND_BASE_URL).rstrip("/")
settings.REQUEST_ID_HEADER = os.getenv("REQUEST_ID_HEADER", settings.REQUEST_ID_HEADER)
settings.API_KEY_HEADER = os.getenv("API_KEY_HEADER", settings.API_KEY_HEADER)

from .auth import APIKeyMiddleware
from .logging_config import setup_logging
from .proxy import get_backend_health
from .rate_limit import RateLimitMiddleware
from .utils import RequestIDMiddleware


app = FastAPI(
    title="API Gateway Troubleshooting Lab",
    description="Simulated API gateway used for troubleshooting integration scenarios",
    version="1.0",
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(APIKeyMiddleware)

logger = setup_logging()


@app.get("/health")
def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "api-gateway",
            "message": "Gateway is running",
        },
    )


@app.post("/orders")
async def create_order(request: Request):
    request_id = request.state.request_id
    content_type = request.headers.get("content-type", "")

    logger.info(
        "Gateway order request received",
        extra={"request_id": request_id},
    )

    if "application/xml" not in content_type.lower():
        logger.warning(
            "Unsupported content type received",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=415,
            content={
                "error": "Unsupported Media Type",
                "message": "Content-Type must be application/xml",
                "request_id": request_id,
            },
        )

    body = await request.body()

    outbound_headers = {
        "Content-Type": "application/xml",
        settings.REQUEST_ID_HEADER: request_id,
    }

    failure_mode = request.headers.get("X-Failure-Mode")
    if failure_mode:
        outbound_headers["X-Failure-Mode"] = failure_mode

    try:
        logger.info(
            "Forwarding order request to backend",
            extra={"request_id": request_id},
        )

        backend_response = requests.post(
            f"{settings.BACKEND_BASE_URL}/api/orders",
            data=body,
            headers=outbound_headers,
            timeout=settings.BACKEND_TIMEOUT_SECONDS,
        )

        logger.info(
            f"Backend order response received: status_code={backend_response.status_code}",
            extra={"request_id": request_id},
        )

        response_headers = {}
        backend_content_type = backend_response.headers.get("content-type")
        if backend_content_type:
            response_headers["Content-Type"] = backend_content_type

        return Response(
            content=backend_response.content,
            status_code=backend_response.status_code,
            headers=response_headers,
        )

    except requests.exceptions.Timeout:
        logger.error(
            "Backend timeout while creating order",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=504,
            content={
                "error": "Gateway Timeout",
                "message": "Backend service timed out",
                "request_id": request_id,
            },
        )

    except requests.exceptions.ConnectionError:
        logger.error(
            "Backend unavailable while creating order",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=502,
            content={
                "error": "Bad Gateway",
                "message": "Backend service unavailable",
                "request_id": request_id,
            },
        )

    except requests.exceptions.RequestException as exc:
        logger.exception(
            f"Unexpected gateway proxy error while creating order: {exc}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=502,
            content={
                "error": "Bad Gateway",
                "message": "Unexpected error while contacting backend service",
                "request_id": request_id,
            },
        )


@app.get("/gateway/health")
def gateway_backend_health(request: Request):
    request_id = request.state.request_id

    logger.info(
        "Gateway request received",
        extra={"request_id": request_id},
    )

    try:
        logger.info(
            "Forwarding request to backend",
            extra={"request_id": request_id},
        )

        backend_response = get_backend_health(request_id)

        logger.info(
            f"Backend response received: status_code={backend_response.status_code}",
            extra={"request_id": request_id},
        )

        return JSONResponse(
            status_code=backend_response.status_code,
            content={
                "backend_status": backend_response.text,
                "request_id": request_id,
            },
        )

    except requests.exceptions.Timeout:
        logger.error(
            "Backend timeout",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=504,
            content={
                "error": "Gateway Timeout",
                "message": "Backend service timed out",
                "request_id": request_id,
            },
        )

    except requests.exceptions.ConnectionError:
        logger.error(
            "Backend unavailable",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=502,
            content={
                "error": "Bad Gateway",
                "message": "Backend service unavailable",
                "request_id": request_id,
            },
        )

    except requests.exceptions.RequestException as exc:
        logger.exception(
            f"Unexpected gateway proxy error: {exc}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=502,
            content={
                "error": "Bad Gateway",
                "message": "Unexpected error while contacting backend service",
                "request_id": request_id,
            },
        )
