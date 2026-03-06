# API Gateway Troubleshooting Lab

A small platform-support style lab that simulates how an API gateway handles authentication, rate limiting, request tracing, and backend proxying in front of an existing backend API.

This project is designed to demonstrate common API gateway troubleshooting scenarios encountered in production environments.

## Architecture

Client  
↓  
API Gateway (FastAPI)  
↓  
Backend Service (Flask API)

The backend service is provided by the companion project:

**API Integration Troubleshooting Lab**

## Features

- API key authentication
- request ID generation and propagation
- rate limiting
- request logging
- backend proxying
- structured error responses

## Failure Scenarios

The lab simulates several common API gateway issues:

- Missing API key → `401 Unauthorized`
- Invalid API key → `403 Forbidden`
- Rate limit exceeded → `429 Too Many Requests`
- Backend unavailable → `502 Bad Gateway`
- Backend timeout → `504 Gateway Timeout`

## Purpose

This project demonstrates troubleshooting workflows across the API platform layer rather than the backend service itself.

It is intended as a companion project to the backend API troubleshooting lab to create a realistic multi-service architecture for debugging and support scenarios.