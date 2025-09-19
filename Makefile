%:
	@:

build:
	docker compose build

run:
	docker compose up --detach

stop:
	docker compose stop

fg_run:
	docker compose up

test:
	docker compose run --rm app pytest

lint:
	docker compose run --rm --no-deps app sh -c "\
		ruff check --fix . && \
		ruff check --fix --select I . && \
		black . && \
		ty check"

check:
	docker compose run --rm --no-deps app sh -c "\
		ruff check  . && \
		ruff check --select I . && \
		black --check .  && \
		ty check"

run_migrations:
	docker compose run --rm --no-deps app alembic upgrade head


create_migrations:
	@msg='$(filter-out $@,$(MAKECMDGOALS))'; \
	docker compose run --rm --no-deps app alembic revision --autogenerate -m "$$msg"

clear_db:
	docker compose rm -f db
	docker volume rm travel-map_pgdata

clean:
	rm -rf tmp

script-save-strava-routes:
	docker compose run --rm app uv run python ./scripts/save_strava_routes.py

### Local section
local_install:
	uv sync

local_run:
	uv run uvicorn travel_map.app:app --reload

local_lint:
	uv run ruff check --fix .
	uv run ruff check --fix --select I .
	uv run black .
	uv run ty check

local_check:
	uv run ruff check .
	uv run ruff check --select I .
	uv run black --check .
	uv run ty check

local_test:
	uv run pytest

l-install: local_install

l-lint: local_lint

l-check: local_check

l-run: local_run

l-test: local_test

lock_dependencies:
	docker compose run --rm --no-deps app uv lock

add_dependency:
	@name='$(filter-out $@,$(MAKECMDGOALS))'; \
	docker compose run --rm --no-deps app uv add $$name

add_dev_dependency:
	@name='$(filter-out $@,$(MAKECMDGOALS))'; \
	docker compose run --rm --no-deps app uv add --dev $$name

remove_dependency:
	@name='$(filter-out $@,$(MAKECMDGOALS))'; \
	docker compose run --rm --no-deps app uv remove $$name

remove_dev_dependency:
	@name='$(filter-out $@,$(MAKECMDGOALS))'; \
	docker compose run --rm --no-deps app uv remove --dev $$name
