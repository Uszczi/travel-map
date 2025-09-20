FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

COPY pyproject.toml .

RUN uv sync --no-dev

COPY . .
RUN uv pip install -e .

CMD ["uv", "run", "--no-sync", "uvicorn", "travel_map.app:app", "--host", "0.0.0.0", "--port", "8000"]
