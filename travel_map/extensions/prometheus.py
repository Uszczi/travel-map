from fastapi import FastAPI
from prometheus_client import CollectorRegistry, make_asgi_app, multiprocess


def make_metrics_app():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


def include_prometheus(app: FastAPI) -> None:
    metrics_app = make_metrics_app()
    app.mount("/metrics", metrics_app)
