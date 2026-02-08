#!/usr/bin/env python3
"""Controller protocol for the adapter layer.

Defines the contract that all controllers must satisfy. State machines
and entry points depend on this protocol; concrete controllers implement
it in the adapter layer.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Controller(Protocol):
    """Contract for application controllers.

    Defines the public interface that state machines and entry
    points depend on. Internal details such as service injection
    and initialisation are handled by the ABC base class.
    """
