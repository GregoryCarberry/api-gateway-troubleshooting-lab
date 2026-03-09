## Troubleshooting Scenarios

This gateway is designed to reproduce several common API platform
failure modes.

### Missing API Key

Request sent without authentication header.

Example:

    curl http://localhost:8000/gateway/health

Response:

    401 Unauthorized

Cause:

Missing API key.

Fix:

    curl -H "X-API-Key: lab-demo-key" http://localhost:8000/gateway/health

------------------------------------------------------------------------

### Invalid API Key

Request sent with an incorrect API key.

Example:

    curl -H "X-API-Key: wrong-key" http://localhost:8000/gateway/health

Response:

    403 Forbidden

Cause:

API key does not match the configured gateway key.

------------------------------------------------------------------------

### Rate Limit Exceeded

Sending too many requests within the configured time window.

Example:

    curl -H "X-API-Key: lab-demo-key" http://localhost:8000/gateway/health

After the allowed number of requests:

    429 Too Many Requests

Cause:

Gateway rate limiter triggered.

------------------------------------------------------------------------

### Backend Service Unavailable

If the backend API server is stopped, the gateway cannot forward
requests.

Example:

Stop the backend server and run:

    curl -H "X-API-Key: lab-demo-key" http://localhost:8000/gateway/health

Response:

    502 Bad Gateway

Cause:

Gateway cannot connect to backend service.

------------------------------------------------------------------------

### Backend Timeout

If the backend does not respond within the configured timeout period,
the gateway returns:

    504 Gateway Timeout

Cause:

Backend service response exceeded the configured timeout.
