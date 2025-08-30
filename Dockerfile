FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .

RUN uv sync
# RUN uv run playwright install && uv run playwright install-deps

COPY . .
RUN uv pip install -e .

CMD ["uv", "run", "uvicorn", "travel_map.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
