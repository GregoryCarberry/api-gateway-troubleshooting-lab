import requests
from .config import BACKEND_BASE_URL, BACKEND_TIMEOUT_SECONDS, REQUEST_ID_HEADER


def get_backend_health(request_id: str):
    return requests.get(
        f"{BACKEND_BASE_URL}/health",
        timeout=BACKEND_TIMEOUT_SECONDS,
        headers={
            REQUEST_ID_HEADER: request_id
        }
    )