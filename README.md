# Travel Map

A FastAPI-based application for generating and analyzing travel routes with elevation profiles, GPX export, and Strava integration.

## Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose (recommended)
- `uv` package manager

### Setup

1. **Clone and configure:**
   ```bash
   cp example.env .env          # Fill in required tokens (LocationIQ, Strava, etc.)
   uv sync                      # Install dependencies
   ```

2. **Run with Docker (recommended):**
   ```bash
   docker compose up --detach   # Start PostgreSQL, Redis, MongoDB, Mailhog, monitoring
   just run                     # Start the app
   ```

3. **Or run locally without Docker:**
   ```bash
   just l-install && just l-run  # Requires .env with all external service credentials
   ```

The app will be available at `http://localhost:8000` with API docs at `http://localhost:8000/docs`.

## Development

### Commands

| Task | Docker | Local |
|------|--------|-------|
| Run app | `just run` | `just l-run` |
| Run tests | `just test` | `just l-test` |
| Lint & fix | `just lint` | `just l-lint` |
| Type check | `just check` | `just l-check` |
| Run migrations | `just run_migrations` | `alembic upgrade head` |
| Create migration | `just create_migrations "message"` | `alembic revision --autogenerate -m "message"` |

### Testing

- Tests use **SQLite in-memory** (no external DB needed)
- Cache is **in-memory** (no Redis needed)
- Auth tests register/log in via API
- All async tests require `@pytest.mark.asyncio`
- Use factory-boy: `acreate_user(session, ...)` in `tests/factories.py`
- Run single file: `uv run pytest tests/api/test_user.py`

### Code Quality

- **Linting & Formatting:** Ruff + Black (line-length: 120)
- **Type Checking:** `ty` (mypy alternative)
- **Import ordering:** isort with `app` as first-party

## Project Structure

```
app/
  api/             # FastAPI routers (thin layer, delegates to use_cases)
  domain/          # Port interfaces (Protocol, ABC)
  use_case/        # Business logic
  infrastructure/  # Implementation: SqlAlchemy, repositories
  services/        # External integrations: elevation, email, gpx, nominatim
  generator/       # Route generation: A*, DFS, random routes
  extensions/      # FastAPI lifespan, Prometheus, SQLAdmin, observability
  models.py        # SQLModel + Pydantic models (UserModel, Route, Segment)
  settings.py      # Environment configuration (pydantic-settings)
  db.py            # Database setup: PostgreSQL, MongoDB, Redis
  jwt.py           # JWT handling (3 secret keys, audience-based)
  password.py      # Argon2 password hashing via pwdlib
  web/             # Frontend templates

migrations/        # Alembic: async migrations
tests/             # pytest fixtures, factories, integration tests
templates/         # Jinja2 email templates (en/, pl/)
deployment/        # Production docker-compose & scripts
```

## Key Features

### Route Generation
- **Algorithms:** A* pathfinding, depth-first search, random route generation
- **Elevation Profiles:** Integrated elevation data
- **GPX Export:** Generate downloadable GPX files

### Authentication & Authorization
- JWT-based with httponly cookies
- Three secret keys: `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, `JWT_EMAIL_SECRET`
- Token types via `aud` claim: `access`, `refresh`, `activation`, `password_reset`

### Integrations
- **Strava:** Import and sync routes from Strava
- **LocationIQ:** Geocoding and reverse geocoding
- **MongoDB:** Route metadata storage
- **PostgreSQL:** User accounts and structured data
- **Redis:** Caching and rate limiting

### Monitoring & Observability
- **OpenTelemetry:** Distributed tracing (OTLP)
- **Prometheus:** Metrics
- **Loki:** Log aggregation
- **Grafana:** Dashboards
- **Sentry:** Error tracking

## Database

### PostgreSQL
- User accounts, routes, segments
- Async SQLModel ORM with Alembic migrations
- Connection: `DB_ASYNC_CONNECTION_STR` from `.env`

### MongoDB
- Route metadata and analysis results
- Raw Strava data
- Connection: `MONGO_URI` from `.env`

### Redis
- Cache backend for route data
- Rate limiting
- Async with `aioredis`

## Environment Variables

Copy `example.env` to `.env` and configure:

```env
# Database
DB_ASYNC_CONNECTION_STR=postgresql+asyncpg://user:pass@localhost/travel_map
MONGO_URI=mongodb://localhost:27017/travel_map
REDIS_URL=redis://localhost:6379

# JWT (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_ACCESS_SECRET=your-secret-key
JWT_REFRESH_SECRET=your-secret-key
JWT_EMAIL_SECRET=your-secret-key

# External APIs
LOCATIONIQ_API_KEY=your-key
STRAVA_CLIENT_ID=your-id
STRAVA_CLIENT_SECRET=your-secret

# Email
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
MAIL_FROM=noreply@travel-map.app

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
SENTRY_DSN=your-sentry-dsn
```

## Deployment

The app is deployed to a VPS via CI/CD:

1. Push to `master` triggers deployment
2. Code is synced via rsync over SSH
3. Docker image is built
4. Migrations run automatically
5. Services start via `deployment/docker-compose.yml`
6. Nginx is updated with new configuration

See `deployment/deploy.sh` for details.

## Frontend

- **Framework:** FastAPI templates with Jinja2
- **Styling:** Tailwind CSS (via CDN)
- **Maps:** Folium for interactive map rendering

## Support

For issues or feedback, visit:
- GitHub Issues: [travel-map issues](https://github.com/anomalyco/opencode)
- Developer setup help: See AGENTS.md

## License

See LICENSE file for details.
