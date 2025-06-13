%:
	@:

build:
	docker compose build

run:
	uv run uvicorn travel_map.app:app --reload

run_docker:
	docker compose up --detach

run_docker_fg:
	docker compose up

lint:
	uv run ruff check --fix .
	uv run ruff check --fix --select I .
	uv run black .

check:
	TODO

docker_lint:
	docker compose run --rm --no-deps app sh -c "\
		uv run ruff check --fix . && \
		uv run ruff check --fix --select I . && \
		uv run black ."

docker_check:
	TODO

d-lint: docker_lint

d-check: docker_check

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
