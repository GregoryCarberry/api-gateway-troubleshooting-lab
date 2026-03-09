# API Gateway Troubleshooting Lab

A lightweight API gateway built with FastAPI that simulates common API
platform failures such as authentication errors, rate limiting, backend
outages, and request tracing.

This repository is part of the **API Troubleshooting Lab Series**, a
multi-service environment designed to demonstrate real-world integration
debugging and platform support scenarios.

------------------------------------------------------------------------

## Lab Series Architecture

This gateway sits in front of the backend API service provided by the
companion project:

**Backend API:**\
https://github.com/GregoryCarberry/api-integration-troubleshooting-lab

Architecture:

Client\
│\
▼\
API Gateway (FastAPI)\
│\
▼\
Backend API (Flask)

The gateway is responsible for:

-   request authentication
-   rate limiting
-   request tracing
-   backend proxying
-   gateway-level error handling

------------------------------------------------------------------------

## Features

The gateway implements several behaviours commonly found in production
API gateways.

### Authentication

Requests must include a valid API key:

    X-API-Key: lab-demo-key

### Rate Limiting

Clients are limited to a fixed number of requests per time window.

Exceeded limits return:

    429 Too Many Requests

### Request Tracing

Each request is assigned a unique request ID:

    X-Request-ID: <uuid>

If a client does not provide a request ID, the gateway generates one
automatically.\
The same request ID is forwarded to the backend service.

### Backend Proxying

Gateway endpoints forward requests to the backend API.

Example:

    GET /gateway/health → GET /health (backend)

### Gateway Error Handling

The gateway converts backend failures into platform-level responses.

  Scenario              Response
  --------------------- -----------------------
  Missing API key       401 Unauthorized
  Invalid API key       403 Forbidden
  Rate limit exceeded   429 Too Many Requests
  Backend unavailable   502 Bad Gateway
  Backend timeout       504 Gateway Timeout

------------------------------------------------------------------------

## Repository Structure

    app/
    ├── main.py              # FastAPI application and routes
    ├── auth.py              # API key middleware
    ├── rate_limit.py        # rate limiting middleware
    ├── utils.py             # request ID middleware
    ├── proxy.py             # backend request forwarding
    ├── config.py            # gateway configuration
    └── logging_config.py    # logging setup

------------------------------------------------------------------------

## Running the Gateway

Clone the repository:

    git clone https://github.com/GregoryCarberry/api-gateway-troubleshooting-lab.git
    cd api-gateway-troubleshooting-lab

Create a virtual environment:

    python3 -m venv venv
    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Run the gateway:

    uvicorn app.main:app --reload

The gateway will be available at:

    http://localhost:8000

------------------------------------------------------------------------

## Example Requests

### Gateway Health

    curl http://localhost:8000/health

### Backend Health via Gateway

    curl -H "X-API-Key: lab-demo-key" http://localhost:8000/gateway/health

### Rate Limit Example

Send multiple requests quickly:

    curl -H "X-API-Key: lab-demo-key" http://localhost:8000/gateway/health

After the limit is reached:

    429 Too Many Requests

------------------------------------------------------------------------

## Purpose

This project demonstrates operational troubleshooting workflows for API
platform layers.

It is designed to simulate the types of issues platform engineers and
technical support teams investigate in real systems, including:

-   authentication failures
-   rate limiting behaviour
-   backend service outages
-   request tracing across services
