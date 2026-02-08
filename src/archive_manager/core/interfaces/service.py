#!/usr/bin/env python3
"""Service protocol for the application layer.

Defines the contract that all services must satisfy. Controllers depend
on this protocol; concrete services implement it in the application layer.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Service(Protocol):
    """Contract for application services.

    Defines the public interface that controllers depend on.
    Internal details such as repository injection and
    initialisation are handled by the ABC base class.

    Attributes:
        NAME: Service name identifier.
    """

    NAME: str
