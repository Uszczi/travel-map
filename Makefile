run:
	uvicorn travel_map.app:app --reload

lint:
	ruff check --fix .
	black .

build:
	docker compose build

run_docker:
	docker compose up --detach


