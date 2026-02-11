# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]
- Dockerized Django + Postgres local environment.
- Added `/api/health/` endpoint for smoke checks.
- Added OpenAPI schema and Swagger UI endpoints.
- Added Postgres healthcheck and dependency gating for the web service.
- Added custom Django auth `User` model (email login + role).
- Added `Ride` and `RideEvent` models.
- Added admin-only JWT token endpoint and protected CRUD endpoints.
