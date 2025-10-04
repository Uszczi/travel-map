set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

COMPOSE        := "docker compose"
APP_SVC        := "app"
DB_SVC         := "db"
PGDATA_VOLUME  := "travel-map_pgdata"
APP_MODULE     := "travel_map.app:app"
BASE_URL       := "http://127.0.0.1:8000"


build:
	{{COMPOSE}} build

run:
	{{COMPOSE}} up --detach

stop:
	{{COMPOSE}} stop

fg_run:
	{{COMPOSE}} up

test:
	{{COMPOSE}} run --rm {{APP_SVC}} pytest

lint:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} sh -lc '\
		ruff check --fix . && \
		ruff check --fix --select I . && \
		black . && \
		ty check \
	'

check:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} sh -lc '\
		ruff check . && \
		ruff check --select I . && \
		black --check . && \
		ty check \
	'

run_migrations:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} alembic upgrade head

create_migrations +msg:
	MSG='{{join(msg, " ")}}'
	if [ -z "$MSG" ]; then
	echo "Please provide a migration message, e.g.: just create_migrations init" >&2
	exit 1
	fi
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} \
		alembic revision --autogenerate -m "$$MSG"

clear_db:
	{{COMPOSE}} rm -fs {{DB_SVC}}
	docker volume rm {{PGDATA_VOLUME}} || true

clean:
	rm -rf tmp

save_strava:
	{{COMPOSE}} run --rm {{APP_SVC}} uv run python ./scripts/save_strava_routes.py

lock_dependencies:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} uv lock

# Dependency management
# Examples:
#   just add fastapi[standard] httpie
#   just add_dev pytest pytest-cov
add +pkgs:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} uv add {{pkgs}}

add_dev +pkgs:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} uv add --dev {{pkgs}}

rm_dep +pkgs:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} uv remove {{pkgs}}

rm_dev_dep +pkgs:
	{{COMPOSE}} run --rm --no-deps {{APP_SVC}} uv remove --dev {{pkgs}}

# -------- Local (no Docker) --------
l-install:
	uv sync

l-run:
	uv run uvicorn {{APP_MODULE}} --reload

l-test:
	uv run pytest

l-lint:
	uv run ruff check --fix .
	uv run ruff check --fix --select I .
	uv run black .
	uv run ty check

l-check:
	uv run ruff check .
	uv run ruff check --select I .
	uv run black --check .
	uv run ty check

l-vulture:
	uv run vulture travel_map \
	  --ignore-decorators "@router.get,@router.post,@router.put,@router.delete,@router.patch,@app.get,@app.post,@app.put,@app.delete,@app.patch"
