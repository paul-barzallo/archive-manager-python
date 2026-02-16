#!/usr/bin/env python3
"""API schemas package."""

from archive_manager.adapters.api.schemas.base import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
)
from archive_manager.adapters.api.schemas.contacts import (
    ContactCreateRequest,
    ContactPageResponse,
    ContactResponse,
    ContactUpdateRequest,
)

__all__ = [
    "ContactCreateRequest",
    "ContactPageResponse",
    "ContactResponse",
    "ContactUpdateRequest",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
]
