from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

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
