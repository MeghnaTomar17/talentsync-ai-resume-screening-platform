"""Common API response envelopes."""

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time: float


def start_timer() -> float:
    return perf_counter()


def build_response(
    *,
    success: bool,
    message: str,
    data: Any = None,
    start_time: float | None = None,
) -> APIResponse[Any]:
    elapsed = 0.0 if start_time is None else round(perf_counter() - start_time, 4)
    return APIResponse(
        success=success,
        message=message,
        data=data,
        processing_time=elapsed,
    )
