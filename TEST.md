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
