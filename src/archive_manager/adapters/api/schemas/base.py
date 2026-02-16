#!/usr/bin/env python3
"""General Pydantic schemas for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error detail payload."""

    code: str
    origin: str
    field: str | None = None
    context: dict[str, object] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Generic API error response."""

    detail: str
    status: int = 400
    errors: list[ErrorDetail] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """API health status response."""

    status: str
    version: str
    database: str
