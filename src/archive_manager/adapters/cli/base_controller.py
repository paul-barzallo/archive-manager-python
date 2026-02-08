#!/usr/bin/env python3
"""Base controller class for the CLI adapter.

Provides a generic abstract base that concrete controllers (e.g.
``ContactCslController``) inherit from. State machines depend on the
``Controller`` protocol defined in ``core.interfaces``; this base class
satisfies that protocol.
"""

from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from archive_manager.core.interfaces import Controller, Service

TService = TypeVar("TService", bound=Service)


class BaseCslController(ABC, Controller, Generic[TService]):
    """Controller that owns its own interaction loop (CLI, TUI).

    Inherits from the ``Controller`` protocol and provides generic
    service typing plus ``__init__`` so that concrete subclasses
    only need to implement business methods.

    Attributes:
        _service: Service instance for business logic.
    """

    _service: TService

    def __init__(self, service: TService) -> None:
        """Initialize the controller with the given service.

        Args:
            service: Service instance for business logic.
        """
        self._service = service
