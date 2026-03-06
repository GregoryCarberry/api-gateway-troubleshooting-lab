from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .auth import APIKeyMiddleware
from .utils import RequestIDMiddleware
from .logging_config import setup_logging
from .rate_limit import RateLimitMiddleware

import requests

app = FastAPI(
    title="API Gateway Troubleshooting Lab",
    description="Simulated API gateway used for troubleshooting integration scenarios",
    version="1.0"
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(APIKeyMiddleware)

BACKEND_BASE_URL = "http://127.0.0.1:5000"

logger = setup_logging()


@app.get("/health")
def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "api-gateway",
            "message": "Gateway is running"
        }
    )


@app.get("/gateway/health")
def gateway_backend_health(request: Request):
    request_id = request.state.request_id

    logger.info(
        "Forwarding request to backend: path=/health request_id=%s",
        request_id
    )

    try:
        backend_response = requests.get(
            f"{BACKEND_BASE_URL}/health",
            timeout=5,
            headers={
                "X-Request-ID": request_id
            }
        )

        logger.info(
            "Backend response received: status_code=%s request_id=%s",
            backend_response.status_code,
            request_id
        )

        return JSONResponse(
            status_code=backend_response.status_code,
            content={
                "backend_status": backend_response.text
            }
        )
    except requests.exceptions.Timeout:
        logger.error(
            "Backend timeout: request_id=%s",
            request_id
        )
        return JSONResponse(
            status_code=504,
            content={"error": "Gateway Timeout", "message": "Backend service timed out"}
        )
    except requests.exceptions.ConnectionError:
        logger.error(
            "Backend unavailable: request_id=%s",
            request_id
        )
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "message": "Backend service unavailable"}
        )