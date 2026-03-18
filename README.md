# API Troubleshooting Lab – Gateway Service

This repository contains the **API gateway** for the API Troubleshooting Lab project.

It sits in front of the backend service and handles the platform concerns that usually shape real troubleshooting work: **authentication, rate limiting, request tracing, proxying, and upstream failure handling**.

This service is designed to help demonstrate how API issues can be reproduced, observed, isolated, and tested across a multi-service system.

---

## Role in the Architecture

```text
Client
  │
  ▼
API Gateway (FastAPI)
  │
  ▼
Backend API (Flask)
  │
  ▼
Response
```

The gateway is responsible for **platform-level controls and cross-service observability**, while the backend handles **application logic and XML validation**.

---

## What This Service Does

The gateway is responsible for:

- enforcing API key authentication
- applying rate limiting controls
- generating and propagating request IDs
- forwarding requests to the backend service
- handling upstream errors such as backend failures and timeouts
- providing a realistic entry point for troubleshooting exercises

---

## Technology

- Python
- FastAPI
- Uvicorn
- Structured JSON logging
- Request correlation via `X-Request-ID`
- Pytest + httpx for test coverage
- Postman for reproducible API demos

---

## Key Features

### Authentication

Requests must include:

```http
X-API-Key: lab-demo-key
```

| Scenario | Status |
|--------|--------|
| missing API key | 401 |
| invalid API key | 403 |

---

### Rate Limiting

Requests are limited within a time window.

Exceeded limits return:

```http
429 Too Many Requests
```

---

### Backend Proxying

The gateway forwards requests to the backend service.

Example:

```text
GET /gateway/health → GET /health (backend)
```

---

### Failure Handling

The gateway converts backend failures into appropriate client responses:

| Scenario | Status |
|--------|--------|
| backend unavailable | 502 |
| backend timeout | 504 |

---

## Endpoints

### `GET /health`

Gateway health check.

```bash
curl http://localhost:8000/health
```

---

### `GET /gateway/health`

Proxies request to backend health endpoint.

```bash
curl -H "X-API-Key: lab-demo-key" http://localhost:8000/gateway/health
```

---

## Observability & Request Tracing

The gateway uses structured logging and request correlation to enable end-to-end tracing across services.

Each incoming request is assigned an `X-Request-ID` if one is not already present. That value is:

- stored for the lifetime of the request
- included in gateway logs
- forwarded to the backend service
- returned in response headers

### Trace Flow

```text
client → gateway → backend → response
```

### Example Response Header

```http
X-Request-ID: 9d966301-ebce-4552-b764-09c498f760f4
```

### Example Gateway Log Output

```json
{
  "timestamp": "2026-03-17T21:00:00.000000",
  "level": "INFO",
  "service": "api-gateway",
  "message": "Gateway request received",
  "request_id": "9d966301-ebce-4552-b764-09c498f760f4"
}
```

### End-to-End Trace Example

A single request can be traced across both gateway and backend services using the same request ID.

**Response header:**

```http
X-Request-ID: 9d966301-ebce-4552-b764-09c498f760f4
```

**Gateway log:**

```json
{
  "message": "Gateway request received",
  "request_id": "9d966301-ebce-4552-b764-09c498f760f4"
}
```

**Backend log:**

```json
{
  "message": "Health check received",
  "request_id": "9d966301-ebce-4552-b764-09c498f760f4"
}
```

### Why This Matters

This enables:

- cross-service troubleshooting
- faster isolation of whether a failure is happening at the gateway or backend layer
- log correlation across services
- a more production-like debugging workflow

---

## Postman Collection

The main demo collection for this project lives in:

```text
postman/api-troubleshooting-lab.postman_collection.json
```

This collection is intentionally **gateway-first**. It reflects how a client would interact with the system in practice and exercises the full request path through the gateway into the backend.

### Included scenarios

- successful request flow
- missing API key (`401`)
- invalid API key (`403`)
- rate limiting (`429`)
- wrong content type (`415`)
- malformed XML (`400`)
- missing required fields (`422`)
- invalid values such as quantity validation failures (`422`)
- simulated backend dependency failure (`503`)
- simulated backend exception (`500`)
- simulated backend timeout surfaced by the gateway (`504`)
- request ID generation and propagation for traceability

### Recommended variables

Use these collection variables in Postman:

```text
base_url = http://127.0.0.1:8000
api_key  = lab-demo-key
```

### Why the collection is here

The collection belongs in the gateway repository because it represents the **main client entry point** into the system.

That makes this repo the most natural place to demonstrate:

- auth behaviour
- gateway controls
- upstream error handling
- end-to-end troubleshooting paths

---

## Running Tests

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
pytest -q
```

### What is covered

- API key authentication (valid / invalid / missing)
- rate limiting behaviour
- gateway → backend proxy behaviour
- upstream timeout and failure handling
- request tracing via `X-Request-ID`
- response propagation from backend

---

## Troubleshooting Workflow Example

```text
Client request fails
↓
Gateway returns 502 or 504
↓
Inspect gateway logs using X-Request-ID
↓
Trace request in backend logs
↓
Identify root cause
↓
Fix request or backend behaviour
```

---

## Running the Gateway

Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the gateway:

```bash
uvicorn app.main:app --reload
```

Gateway runs on:

```text
http://localhost:8000
```

---

## Project Context

This service is part of the **API Troubleshooting Lab** multi-repository project.

The full architecture, diagrams, and cross-repository documentation are maintained in the hub repository:

```text
api-troubleshooting-lab
```
