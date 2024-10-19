run:
	uvicorn travel_map.app:app --reload

lint:
	ruff . --select F401 --fix
	black .
