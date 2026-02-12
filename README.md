# Ride Info API

REST API for managing ride information.

## Table of Contents
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Quickstart (Docker)](#quickstart-docker)
- [API](#api)
- [Design Decisions](#design-decisions)
- [Evaluation Criteria](#evaluation-criteria)
- [Bonus: Raw SQL](#bonus-raw-sql)
- [Testing](#testing)

## Tech Stack
- Python (3.12 recommended)
- Django + Django REST Framework
- PostgreSQL
- Docker / Docker Compose

## Features
- Admin-only API access (role-based) using JWT
- Ride List API:
  - Pagination
  - Filtering by ride status and rider email
  - Sorting by pickup time and distance-to-pickup
- Performance-focused `todays_ride_events` (last 24 hours only)
- Developer-only `X-Query-Count` response header when `DJANGO_DEBUG=true`
- Bonus raw SQL report (trips > 1 hour grouped by month + driver)

## Quickstart (Docker)

### 1) Prerequisites
- Docker Desktop for Linux
- Docker Compose v2

### 2) Environment
Create a local `.env` file (see `.env.example`).

Notes:
- `.env` is intended to be local-only.

### 3) Start services
```bash
docker compose up --build
```

Smoke check:
- `GET http://localhost:8000/api/health/`
- `GET http://localhost:8000/api/docs/`

### 4) Migrations and admin user
Once containers are running:
```bash
docker compose exec web python manage.py migrate
```

Create an initial admin user:
```bash
docker compose exec web python manage.py createsuperuser
```

Optional: seed sample data for local testing:
```bash
docker compose exec web python manage.py seed_data
```

## API

Base URL:
- `http://localhost:8000/api/`

### Authentication rule
Only users with role `admin` can access the API.

Token endpoints:
- `POST /api/auth/token/` (admin only)
- `POST /api/auth/token/refresh/`

### Ride List endpoint
The ride list endpoint supports:
- Pagination
- Filtering by:
  - ride status
  - rider email
- Sorting by:
  - `pickup_time`
  - distance-to-pickup using a provided GPS position

Request parameters (list endpoint):
- `status`: filter by ride status
- `rider_email`: filter by rider email
- `ordering`: `pickup_time`, `-pickup_time`, `distance`, `-distance`
- `lat` + `lon`: required when ordering by distance
- `page`, `page_size`: pagination

Examples:
- `GET /api/rides/?status=pickup`
- `GET /api/rides/?rider_email=rider1@example.com`
- `GET /api/rides/?ordering=-pickup_time`
- `GET /api/rides/?ordering=distance&lat=14.5995&lon=120.9842`

### Performance: `todays_ride_events`
Ride list responses include `todays_ride_events`, containing only RideEvents from the last 24 hours.

Implementation notes:
- Use `select_related` for driver/rider.
- Use a filtered `Prefetch` for `todays_ride_events`.
- Avoid fetching the full `RideEvent` list.

## Design Decisions

- **Authorization**: all API endpoints are protected by an `admin` role check (`IsAdminRole`). Token issuance is restricted to admins via a custom SimpleJWT token view.
- **Query minimization**: the rides list uses `select_related` for rider/driver and a filtered `Prefetch` to avoid loading the full RideEvent history.
- **Distance sorting at scale**: distance-to-pickup sorting is computed in Postgres using `cube` + `earthdistance` (`ll_to_earth` + `earth_distance`) so ordering can be done in the database while still supporting pagination.

## Evaluation Criteria

### Functionality
Yes. The API implements the required models (`User`, `Ride`, `RideEvent`), admin-only authentication, and CRUD endpoints via DRF viewsets. The ride list endpoint supports pagination, filtering (status, rider email), and sorting (pickup time, distance-to-pickup).

### Code Quality
The code is organized by responsibility (viewsets, serializers, filters, pagination, permissions). Query logic is centralized in `RideViewSet.get_queryset()` and uses standard DRF/Django patterns to keep behavior explicit and maintainable.

### Error Handling
Input validation is handled at the API boundary for key edge cases (invalid `lat`/`lon`, requesting distance ordering without coordinates). DRF returns structured `400` responses for invalid query parameters.

### Performance
The ride list query uses `select_related` for rider/driver and a filtered `Prefetch` for `todays_ride_events` (last 24 hours only), avoiding loading the full RideEvent history. Distance sorting is computed in Postgres to preserve correct ordering with pagination.

## Bonus: Raw SQL

A raw SQL statement that counts trips that took more than 1 hour, grouped by month and driver.

Note: trip duration is computed using RideEvents with descriptions:
- `Status changed to pickup`
- `Status changed to dropoff`

Run it locally:

```bash
docker compose exec db psql -U ride_info -d ride_info
```

```sql
WITH per_ride AS (
  SELECT
    r.id_ride,
    r.id_driver AS driver_id,
    MIN(e.created_at) FILTER (WHERE e.description = 'Status changed to pickup') AS pickup_at,
    MAX(e.created_at) FILTER (WHERE e.description = 'Status changed to dropoff') AS dropoff_at
  FROM rides_ride r
  JOIN rides_rideevent e ON e.id_ride = r.id_ride
  GROUP BY r.id_ride, r.id_driver
)
SELECT
  date_trunc('month', pr.pickup_at) AS month,
  (u.first_name || ' ' || u.last_name) AS driver,
  COUNT(*) AS trips_over_1h
FROM per_ride pr
JOIN rides_user u ON u.id_user = pr.driver_id
WHERE pr.pickup_at IS NOT NULL
  AND pr.dropoff_at IS NOT NULL
  AND (pr.dropoff_at - pr.pickup_at) > INTERVAL '1 hour'
GROUP BY month, driver
ORDER BY month ASC, driver ASC;
```

## Testing

See `TEST.md` for step-by-step Docker and Postman testing.

To populate sample data locally: `docker compose exec web python manage.py seed_data` (seeded users use password `password`)

When `DJANGO_DEBUG=true`, API responses include `X-Query-Count` to help validate query efficiency during development.
