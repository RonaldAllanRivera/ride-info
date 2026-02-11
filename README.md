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

### 3) Start services
```bash
docker compose up --build
```

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

### Ride List endpoint requirements
The ride list endpoint supports:
- Pagination
- Filtering by:
  - ride status
  - rider email
- Sorting by:
  - `pickup_time`
  - distance-to-pickup using a provided GPS position

### Performance: `todays_ride_events`
Ride list responses include `todays_ride_events`, containing only RideEvents from the last 24 hours.

Implementation notes:
- Use `select_related` for driver/rider.
- Use a filtered `Prefetch` for `todays_ride_events`.
- Avoid fetching the full `RideEvent` list.

## Bonus: Raw SQL

A raw SQL statement that counts trips that took more than 1 hour (pickup -> dropoff), grouped by month and driver, will be included here after the schema is implemented.
