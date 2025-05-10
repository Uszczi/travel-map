run:
	uvicorn travel_map.app:app --reload

run_docker:
	docker compose up --detach

run_docker_fg:
	docker compose up

lint:
	ruff check --fix .
	isort .
	black .

check:
	TODO

docker_lint:
	TODO:

docker_check:
	TODO

build:
	docker compose build
