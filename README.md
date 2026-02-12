# Ride Info API

REST API for managing ride information.

## Tech Stack
- Python (3.12 recommended)
- Django + Django REST Framework
- PostgreSQL
- Docker / Docker Compose

## Local Setup (Ubuntu + Docker Desktop)

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

## API Notes

### Authentication rule
Only users with role `admin` can access the API.

Token endpoints:
- `POST /api/auth/token/` (admin only)
- `POST /api/auth/token/refresh/`

### Ride List endpoint requirements
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

### Performance: `todays_ride_events`
Ride list responses include `todays_ride_events`, containing only RideEvents from the last 24 hours.

Implementation notes:
- Use `select_related` for driver/rider.
- Use a filtered `Prefetch` for `todays_ride_events`.
- Avoid fetching the full `RideEvent` list.

## Bonus: Raw SQL

A raw SQL statement that counts trips that took more than 1 hour (pickup -> dropoff), grouped by month and driver, will be included here after the schema is implemented.

## Testing

See `TEST.md` for step-by-step Docker and Postman testing.

To populate sample data locally: `docker compose exec web python manage.py seed_data` (seeded users use password `password`)
