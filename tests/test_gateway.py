from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
import requests

# Import actual FastAPI app
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app as gateway_app  # noqa: E402
from app.rate_limit import client_requests  # noqa: E402


VALID_ORDER_XML = b"""<Order>
  <CustomerID>CUST-1001</CustomerID>
  <ProductID>PROD-2002</ProductID>
  <Quantity>3</Quantity>
</Order>
"""


class DummyResponse:
    def __init__(self, status_code: int, content: bytes, headers: dict[str, str] | None = None):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {"content-type": "application/xml"}


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("BACKEND_URL", "http://backend:5000")

    client_requests.clear()

    with TestClient(gateway_app) as test_client:
        yield test_client

    client_requests.clear()


def _auth_headers(api_key: str = "test-key", request_id: str | None = None):
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/xml",
    }
    if request_id:
        headers["X-Request-ID"] = request_id
    return headers


def test_health(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_requires_api_key(client: TestClient):
    response = client.post(
        "/orders",
        content=VALID_ORDER_XML,
        headers={"Content-Type": "application/xml"},
    )

    assert response.status_code == 401


def test_invalid_api_key(client: TestClient):
    response = client.post(
        "/orders",
        content=VALID_ORDER_XML,
        headers=_auth_headers(api_key="wrong-key"),
    )

    assert response.status_code == 403


def test_proxy_success(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    def fake_post(*args: Any, **kwargs: Any):
        headers = kwargs.get("headers", {})
        return DummyResponse(
            201,
            b"<OrderCreated><OrderID>abc123</OrderID></OrderCreated>",
            {"content-type": "application/xml", "x-request-id": headers.get("X-Request-ID", "test")},
        )

    monkeypatch.setattr(requests, "post", fake_post)

    response = client.post(
        "/orders",
        content=VALID_ORDER_XML,
        headers=_auth_headers(),
    )

    assert response.status_code == 201
    assert b"<OrderCreated>" in response.content


def test_proxy_failure(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    def fake_post(*args: Any, **kwargs: Any):
        return DummyResponse(503, b"Service Unavailable")

    monkeypatch.setattr(requests, "post", fake_post)

    response = client.post(
        "/orders",
        content=VALID_ORDER_XML,
        headers=_auth_headers(),
    )

    assert response.status_code == 503


def test_rate_limit(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    def fake_post(*args: Any, **kwargs: Any):
        return DummyResponse(201, b"ok")

    monkeypatch.setattr(requests, "post", fake_post)

    statuses = []
    for _ in range(5):
        res = client.post(
            "/orders",
            content=VALID_ORDER_XML,
            headers=_auth_headers(),
        )
        statuses.append(res.status_code)

    assert statuses[:3] == [201, 201, 201]
    assert 429 in statuses
