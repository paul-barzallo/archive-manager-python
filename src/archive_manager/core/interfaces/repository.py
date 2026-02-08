#!/usr/bin/env python3
"""Base repository protocol for the persistence layer.

Provides a minimal marker contract to keep layer boundaries explicit
and consistent. Concrete repository protocols (e.g. ``ContactRepository``)
extend this with domain-specific operations.

The core layer does NOT reference infrastructure details such as
database connections — those are implementation concerns handled by
the infrastructure layer.
"""

from typing import Protocol


class Repository(Protocol):
    """Marker protocol for repositories."""

    ...
