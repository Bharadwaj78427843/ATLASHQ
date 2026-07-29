"""
app/ai/telemetry/hooks.py

Observability hooks the AI platform calls into. These are intentionally
vendor-neutral — no OpenTelemetry/Datadog/etc. SDK is imported here.
Wiring a real backend means implementing these protocols and registering
the implementation at app startup; nothing in the platform changes.
"""
from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator, Protocol


class TracingHook(Protocol):
    """Distributed tracing sink."""

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Any: ...

    def end_span(self, span: Any, error: BaseException | None = None) -> None: ...


class MetricsHook(Protocol):
    """Metrics sink for counters/gauges/histograms."""

    def record_latency(self, name: str, seconds: float, tags: dict[str, str] | None = None) -> None: ...

    def record_count(self, name: str, value: int = 1, tags: dict[str, str] | None = None) -> None: ...

    def record_token_usage(
        self, provider: str, prompt_tokens: int, completion_tokens: int, tags: dict[str, str] | None = None
    ) -> None: ...

    def record_cost(self, provider: str, amount: float, currency: str = "USD", tags: dict[str, str] | None = None) -> None: ...


class LoggingHook(Protocol):
    """Structured logging sink."""

    def log(self, level: str, message: str, **fields: Any) -> None: ...


class NoOpTracingHook:
    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Any:
        return None

    def end_span(self, span: Any, error: BaseException | None = None) -> None:
        return None


class NoOpMetricsHook:
    def record_latency(self, name: str, seconds: float, tags: dict[str, str] | None = None) -> None:
        return None

    def record_count(self, name: str, value: int = 1, tags: dict[str, str] | None = None) -> None:
        return None

    def record_token_usage(
        self, provider: str, prompt_tokens: int, completion_tokens: int, tags: dict[str, str] | None = None
    ) -> None:
        return None

    def record_cost(self, provider: str, amount: float, currency: str = "USD", tags: dict[str, str] | None = None) -> None:
        return None


class StdlibLoggingHook:
    """Default `LoggingHook` backed by the standard library `logging` module."""

    def __init__(self, logger_name: str = "atlas.ai") -> None:
        self._logger = logging.getLogger(logger_name)

    def log(self, level: str, message: str, **fields: Any) -> None:
        self._logger.log(getattr(logging, level.upper(), logging.INFO), "%s | %s", message, fields)


@dataclass
class TelemetryContext:
    """Bundle of hooks passed to providers/orchestration. Defaults to no-ops."""

    tracing: TracingHook = field(default_factory=NoOpTracingHook)
    metrics: MetricsHook = field(default_factory=NoOpMetricsHook)
    logging_hook: LoggingHook = field(default_factory=StdlibLoggingHook)

    @contextmanager
    def timed(self, name: str, tags: dict[str, str] | None = None) -> Iterator[None]:
        """Context manager that records span + latency for a block of work."""
        span = self.tracing.start_span(name, tags)
        started = time.perf_counter()
        error: BaseException | None = None
        try:
            yield
        except BaseException as exc:  # noqa: BLE001 - re-raised below
            error = exc
            raise
        finally:
            elapsed = time.perf_counter() - started
            self.metrics.record_latency(name, elapsed, tags)
            self.tracing.end_span(span, error)


_default_context = TelemetryContext()


def get_telemetry() -> TelemetryContext:
    """Return the process-wide default `TelemetryContext` (all no-ops until wired)."""
    return _default_context
