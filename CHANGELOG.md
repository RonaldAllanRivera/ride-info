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
- Implemented optimized Ride List API (pagination, filtering, sorting by pickup time and distance-to-pickup).
- Added `todays_ride_events` (last 24 hours only) via filtered prefetch for performance.
- Enabled Postgres `cube` + `earthdistance` extensions and added supporting indexes.
- Added `seed_data` management command for generating sample users, rides, and ride events.
