FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID app && useradd -m -u $UID -g $GID app
RUN chown -R app:app /app
USER app

COPY . .
RUN uv pip install -e .

CMD ["uv", "run", "uvicorn", "travel_map.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
