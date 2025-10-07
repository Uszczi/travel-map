import json
import os
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Optional, cast

from fastapi import FastAPI, Request, Response
from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, Status, StatusCode

SERVICE_NAME = os.getenv("SERVICE", "demo-app")
ENV = os.getenv("ENV", "dev")
VERSION = os.getenv("VERSION", "local")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4318")
OTLP_HEADERS = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")

trace_id_var: ContextVar[Optional[str]] = cast(
    ContextVar[Optional[str]], ContextVar("trace_id", default=None)
)
span_id_var: ContextVar[Optional[str]] = cast(
    ContextVar[Optional[str]], ContextVar("span_id", default=None)
)
correlation_id_var: ContextVar[Optional[str]] = cast(
    ContextVar[Optional[str]], ContextVar("correlation_id", default=None)
)


def set_ids_from_span(span: Optional[Span]) -> None:
    if span is None or not span.get_span_context().is_valid:
        trace_id_var.set(None)
        span_id_var.set(None)
        return
    sc = span.get_span_context()

    trace_id_var.set(f"{sc.trace_id:032x}")
    span_id_var.set(f"{sc.span_id:016x}")


def json_sink(message):
    r = message.record
    payload = {
        "timestamp": r["time"].isoformat(),
        "level": r["level"].name,
        "message": r["message"],
        "module": r["module"],
        "function": r["function"],
        "line": r["line"],
        "trace_id": r["extra"].get("trace_id") or trace_id_var.get(),
        "span_id": r["extra"].get("span_id") or span_id_var.get(),
        "correlation_id": r["extra"].get("correlation_id") or correlation_id_var.get(),
        "env": ENV,
        "service": SERVICE_NAME,
        "version": VERSION,
        "http_method": r["extra"].get("http_method"),
        "http_path": r["extra"].get("http_path"),
        "http_status": r["extra"].get("http_status"),
        "duration_ms": r["extra"].get("duration_ms"),
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


async def logging_tracing_middleware(request: Request, call_next):
    corr = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    correlation_id_var.set(corr)

    span = trace.get_current_span()
    set_ids_from_span(span)

    start = time.perf_counter()
    try:
        response: Response = await call_next(request)
        span.set_attribute("http.response.status_code", response.status_code)
        return response
    except Exception as exc:
        span.record_exception(exc)
        span.set_status(Status(StatusCode.ERROR, str(exc)))
        logger.bind(
            trace_id=trace_id_var.get(),
            span_id=span_id_var.get(),
            correlation_id=corr,
            http_method=request.method,
            http_path=request.url.path,
        ).error(f"Unhandled exception: {exc!r}")
        raise
    finally:
        dur_ms = round((time.perf_counter() - start) * 1000, 2)
        if "response" in locals():
            span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("app.duration_ms", dur_ms)
        logger.bind(
            trace_id=trace_id_var.get(),
            span_id=span_id_var.get(),
            correlation_id=corr,
            http_method=request.method,
            http_path=request.url.path,
            http_status=(response.status_code if "response" in locals() else None),
            duration_ms=dur_ms,
        ).info("HTTP request handled")


def include_alloy(app: FastAPI) -> None:
    if getattr(app.state, "alloy_initialized", False):
        return

    logger.remove()
    logger.add(json_sink, level=LOG_LEVEL, backtrace=False, diagnose=False)

    resource = Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.version": VERSION,
            "deployment.environment": ENV,
        }
    )
    provider = TracerProvider(resource=resource)

    if OTLP_HEADERS:
        headers_dict = dict(h.split("=", 1) for h in OTLP_HEADERS.split(","))
    else:
        headers_dict = {}

    exporter = OTLPSpanExporter(
        endpoint=f"{OTLP_ENDPOINT.rstrip('/')}/v1/traces",
        headers=headers_dict,
    )
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    RequestsInstrumentor().instrument()

    app.middleware("http")(logging_tracing_middleware)

    app.state.alloy_initialized = True
