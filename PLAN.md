# Plan

## Phase 1 — Foundation (repo, runtime, docs)
- Define the tech stack and project layout.
- Docker-first local environment for Ubuntu (Docker Desktop): Django API + Postgres.
- Add baseline repo hygiene:
  - `.gitignore`
  - `README.md`
  - `CHANGELOG.md`
  - `.env.example` (and `.env` locally)

## Phase 2 — Domain model + authentication
- Implement `User`, `Ride`, `RideEvent` models matching the provided schema.
- Add DRF + authentication so that only users with role `admin` can access the API.
  - Prefer JWT (stateless, works well with APIs) or TokenAuth.
- Add basic admin and management commands to create an initial admin user.

## Phase 3 — Ride List API (correctness + performance)
- Implement CRUD endpoints via DRF viewsets.
- Implement Ride List API:
  - Pagination
  - Filtering by ride `status` and rider `email`
  - Sorting by `pickup_time`
  - Sorting by distance-to-pickup given an input GPS position
- Performance requirements:
  - Return `todays_ride_events` containing only events from the last 24 hours.
  - Avoid joining / fetching the full `RideEvent` list.
  - Use `select_related` for `id_driver`/`id_rider` and a filtered `Prefetch` for `todays_ride_events`.
  - Keep list retrieval to ~2 queries (+1 for count when paginating).

## Phase 4 — Quality, developer experience, and delivery
- Add seed data helper (management command) for fast local testing.
- Add request/response examples and query parameter documentation.
- Add a short performance note: indexing suggestions + how query-count is minimized.
- Add the bonus raw SQL statement to the README.
- Final pass on commit history and a 5-minute walkthrough script.
