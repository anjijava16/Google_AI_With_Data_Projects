"""OpenTelemetry wiring to Cloud Trace.

Generic HTTP tracing tells you a request took 4.2 seconds. For an agent that is
useless — you need to know it was three Gemini calls, one of which retried, plus
a BigQuery scan. So we add agent-specific span attributes alongside the standard
ones.

Cost note: sample aggressively in production. Every tool call is a span and a
busy agent generates a lot of them.
"""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager

log = logging.getLogger(__name__)
_tracer = None


def init_tracing(service_name: str = "dia-agent") -> None:
    global _tracer
    if _tracer is not None:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

        ratio = float(os.getenv("OTEL_SAMPLE_RATIO", "0.1"))
        provider = TracerProvider(
            resource=Resource.create({"service.name": service_name}),
            sampler=TraceIdRatioBased(ratio),
        )
        provider.add_span_processor(BatchSpanProcessor(CloudTraceSpanExporter()))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        log.info("Cloud Trace enabled (sample ratio %.2f)", ratio)
    except Exception:
        log.warning("Tracing unavailable; continuing without it", exc_info=True)


@contextmanager
def span(name: str, **attributes):
    """Span with agent-shaped attributes. No-op if tracing failed to init."""
    if _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(name) as s:
        for key, value in attributes.items():
            if value is not None:
                s.set_attribute(f"agent.{key}", value)
        yield s
