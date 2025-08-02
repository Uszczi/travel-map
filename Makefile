%:
	@:

build:
	docker compose build

install:
	uv sync

run:
	uv run uvicorn travel_map.app:app --reload

lint:
	uv run ruff check --fix .
	uv run ruff check --fix --select I .
	uv run black .
	uv run ty check

check:
	TODO

benchmarks:
	uv run pytest -s tests/benchmarks

docker_run:
	docker compose up --detach

docker_test:
	docker compose run --rm app pytest

docker_fg_run:
	docker compose up

docker_lint:
	docker compose run --rm --no-deps app sh -c "\
		ruff check --fix . && \
		ruff check --fix --select I . && \
		black . && \
		ty check"

docker_check:
	TODO

docker_benchamark:
	docker compose run --rm --no-deps app pytest -v -s tests/benchmarks

d-benchmark: docker_benchamark

d-lint: docker_lint

d-check: docker_check

d-run: docker_run

d-fg-run: docker_fg_run

d-test: docker_test

lock_dependencies:
	docker compose run --rm --no-deps app uv lock

add_dependency:
	@name=$$(echo $(MAKECMDGOALS) | cut -d' ' -f2); \
	docker compose run --rm --no-deps app uv add $$name

add_dev_dependency:
	@name=$$(echo $(MAKECMDGOALS) | cut -d' ' -f2); \
	docker compose run --rm --no-deps app uv add --dev $$name

remove_dependency:
	@name=$$(echo $(MAKECMDGOALS) | cut -d' ' -f2); \
	docker compose run --rm --no-deps app uv remove $$name

remove_dev_dependency:
	@name=$$(echo $(MAKECMDGOALS) | cut -d' ' -f2); \
	docker compose run --rm --no-deps app uv remove --dev $$name
