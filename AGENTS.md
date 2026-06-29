# travel-map

> [!IMPORTANT]
> **Everything must be done through Docker.** For any running, testing, linting, checking, or migration task, agents **must** use the Docker/`just` commands instead of running them locally.

## Quick start

```bash
cp example.env .env          # then fill in tokens
uv sync                      # install deps
uv run uvicorn app.app:app --reload   # dev server
```

Docker: `docker compose up --detach` (needs `.env`, starts Postgres/Redis/MongoDB/Mailhog + monitoring stack).

## Commands

| what | docker | local |
|------|--------|-------|
| run app | `just run` | `just l-run` |
| test | `just test` | `just l-test` |
| lint+fix | `just lint` | `just l-lint` |
| check (no fix) | `just check` | `just l-check` |
| migrations | `just run_migrations` | `alembic upgrade head` |
| new migration | `just create_migrations "msg"` | `alembic revision --autogenerate -m "msg"` |

## Testing

- Tests use **SQLite** in-memory (settings overridden in `tests/conftest.py`), no real DB needed
- Cache is in-memory (`InMemoryBackend`), no Redis needed
- Auth tests register/log in via API — no pre-seeded users
- All async tests need `@pytest.mark.asyncio`
- Factories: `acreate_user(session, ...)` in `tests/factories.py`
- Run single file: `uv run pytest tests/api/test_user.py`

## Project structure

```
app/
  api/             # FastAPI routers (thin, delegate to use_cases/services)
  domain/          # Port interfaces (Protocol, ABC)
  use_case/        # Business logic
  infrastructure/  # Impl: SqlAlchemyUoW, SqlUserRepository
  services/        # elevation, email, gpx, nominatim
  generator/       # Route generation: astar, dfs, random_route
  extensions/      # FastAPI lifespan, prometheus, sqladmin, alloy
  models.py        # SQLModel (UserModel) + Pydantic (Route, Segment, StravaRoute)
  settings.py      # pydantic-settings, reads .env
  db.py            # MongoClient + SQLModel engines + async_session
  jwt.py           # JWT issue/decode (3 secret keys, aud-based)
  password.py      # Argon2 via pwdlib
migrations/        # Alembic (async, reads DB_ASYNC_CONNECTION_STR from env)
tests/             # pytest, factory-boy, httpx AsyncClient
templates/         # Jinja2 email templates (en/, pl/)
```

## Dev services

Start via `docker compose up --detach` (PostgreSQL, Redis, MongoDB, Mailhog). For local dev without Docker, run: `just l-install && just l-run`. Requires `.env` with working secrets for LocationIQ, etc.

## Style

- Ruff + Black (line-length 120), isort first-party: `app`
- Type checking with `ty`
- `uv package = true` (project is a package)
- `app` is known-first-party import
- Tailwind CSS is used (via CDN in templates) — not optional

## JWT auth

Three separate secrets (`JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, `JWT_EMAIL_SECRET`). Token types distinguished by `aud` claim (`access`/`refresh`/`activation`/`password_reset`). Tokens can come via Bearer header or httponly cookie.

## Deployment

CI pushes `master` to VPS via rsync over SSH, then runs `deployment/deploy.sh`: copies `.env`, builds Docker, runs migrations, updates nginx, starts services in `deployment/docker-compose.yml`.
