"""Bounded retry wrapper for a separately provisioned checkpoint service.

Publish retries are allowed only when the service explicitly guarantees
idempotency for repeated identical payload bytes. Verification is read-only and
may be retried on transient connection/timeout failures.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .audit_checkpoint import ExternalCheckpointProvider


class RetryingCheckpointProvider:
    def __init__(self, provider: ExternalCheckpointProvider, *, attempts: int = 3,
                 backoff_seconds: float = 0.25, sleep: Callable[[float], None] | None = None,
                 retryable: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError)) -> None:
        if attempts < 1:
            raise ValueError("attempts must be at least one")
        if backoff_seconds < 0:
            raise ValueError("backoff_seconds cannot be negative")
        if not retryable or any(not isinstance(item, type) or not issubclass(item, BaseException) for item in retryable):
            raise ValueError("retryable must be a nonempty tuple of exception types")
        self._provider = provider
        self._attempts = attempts
        self._backoff = backoff_seconds
        self._sleep = sleep or __import__("time").sleep
        self._retryable = retryable

    def publish_checkpoint(self, payload: bytes) -> str:
        max_attempts = self._attempts if getattr(self._provider, "supports_idempotent_publish", False) is True else 1
        return self._invoke(self._provider.publish_checkpoint, payload, max_attempts=max_attempts)

    def verify_checkpoint(self, payload: bytes, external_reference: str) -> bool:
        return self._invoke(self._provider.verify_checkpoint, payload, external_reference,
                            max_attempts=self._attempts)

    def _invoke(self, operation: Callable[..., Any], *args: Any, max_attempts: int) -> Any:
        for attempt in range(1, max_attempts + 1):
            try:
                return operation(*args)
            except self._retryable:
                if attempt >= max_attempts:
                    raise
                self._sleep(self._backoff * (2 ** (attempt - 1)))

