# Testing

## Prerequisites
- Docker Desktop for Linux
- Docker Compose v2
- Postman

## 1) Boot the stack
From the project root:
```bash
docker compose up --build
```

If you already have containers running and want a clean restart:
```bash
docker compose down
docker compose up --build
```

## 2) Apply migrations
In a second terminal:
```bash
docker compose exec web python manage.py migrate
```

If you are switching to the custom user model for the first time:
```bash
docker compose down -v
docker compose up --build
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

## 3) Smoke tests (no authentication required yet)

### Health endpoint
In Postman:
- Method: `GET`
- URL: `http://localhost:8000/api/health/`

Expected:
- Status: `200 OK`
- Body:
```json
{"status":"ok"}
```

### API docs
Open in browser:
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## 4) Authentication tests (admin-only)

Create an admin user:
```bash
docker compose exec web python manage.py createsuperuser
```

### Obtain JWT token (admin only)
In Postman:
- Method: `POST`
- URL: `http://localhost:8000/api/auth/token/`
- Body: `raw` -> `JSON`

```json
{
  "email": "your-admin-email@example.com",
  "password": "yourpassword"
}
```

Expected:
- Status: `200 OK`
- JSON contains `access` and `refresh`

If the password is incorrect:
- Status: `401 Unauthorized`

Notes:
- The trailing slash matters (`/api/auth/token/`).

### Call an admin-only endpoint
- Method: `GET`
- URL: `http://localhost:8000/api/users/`
- Header: `Authorization: Bearer <access>`

### Ride list (filters + sorting)

List rides (default ordering):
- Method: `GET`
- URL: `http://localhost:8000/api/rides/`

Filter by status:
- `GET http://localhost:8000/api/rides/?status=pickup`

Filter by rider email:
- `GET http://localhost:8000/api/rides/?rider_email=rider1@example.com`

Sort by pickup time:
- `GET http://localhost:8000/api/rides/?ordering=pickup_time`
- `GET http://localhost:8000/api/rides/?ordering=-pickup_time`

Sort by distance to pickup (requires GPS input):
- `GET http://localhost:8000/api/rides/?ordering=distance&lat=14.5995&lon=120.9842`
- `GET http://localhost:8000/api/rides/?ordering=-distance&lat=14.5995&lon=120.9842`

If `DJANGO_DEBUG=true`, check the response header `X-Query-Count` to verify query efficiency.

## 5) Seed sample data (local development)

If `/api/rides/` is empty, seed sample Users, Rides, and RideEvents:

```bash
docker compose exec web python manage.py seed_data
```

Options:
- `--rides 50`
- `--events-per-ride 6`
- `--force` (adds more data even if rides already exist)

Seeded users have password:
- `password`

Seeded test emails (by default):
- Riders: `rider1@example.com` ... `rider10@example.com`
- Drivers: `driver1@example.com` ... `driver5@example.com`

## 6) Bonus SQL (run in Postgres)

Open a psql shell in the database container:

```bash
docker compose exec db psql -U ride_info -d ride_info
```

Run the bonus SQL query from `README.md`.

### How to test the Bonus SQL (step-by-step)

1) Ensure there is at least one ride with events spanning > 1 hour:

```bash
docker compose exec web python manage.py seed_data --force --rides 1 --events-per-ride 1
```

2) Open a Postgres shell:

```bash
docker compose exec db psql -U ride_info -d ride_info
```

3) Paste the Bonus SQL from `README.md` and execute it (make sure it ends with `;`).

Expected:
- At least one row with columns `month`, `driver`, and `trips_over_1h`.

4) If you get 0 rows, run this diagnostic query to find the longest rides:

```sql
SELECT
  r.id_ride,
  r.id_driver AS driver_id,
  MIN(e.created_at) FILTER (WHERE e.description = 'Status changed to pickup') AS pickup_at,
  MAX(e.created_at) FILTER (WHERE e.description = 'Status changed to dropoff') AS dropoff_at,
  (MAX(e.created_at) FILTER (WHERE e.description = 'Status changed to dropoff')
    - MIN(e.created_at) FILTER (WHERE e.description = 'Status changed to pickup')) AS duration
FROM rides_ride r
JOIN rides_rideevent e ON e.id_ride = r.id_ride
GROUP BY r.id_ride, r.id_driver
HAVING MIN(e.created_at) FILTER (WHERE e.description = 'Status changed to pickup') IS NOT NULL
   AND MAX(e.created_at) FILTER (WHERE e.description = 'Status changed to dropoff') IS NOT NULL
ORDER BY duration DESC
LIMIT 10;
```

Exit psql:

```sql
\q
```

Notes:
- The included `seed_data` command ensures at least one ride has events spanning > 1 hour so the query returns rows.
- If you seeded before this behavior was added, re-run: `docker compose exec web python manage.py seed_data --force`

## 4) Troubleshooting

### Database not ready when running migrations
Symptoms:
- `psycopg.OperationalError` / connection refused

Fix:
- Wait a few seconds and run the migrate command again:
```bash
docker compose exec web python manage.py migrate
```

### Port conflicts
If ports are already in use:
- Update `docker-compose.yml` port mappings (e.g. `8001:8000`), then rerun:
```bash
docker compose down
docker compose up --build
```
