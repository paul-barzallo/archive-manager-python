#!/usr/bin/env python3
"""CLI adapter layer — console-based delivery mechanism."""

from archive_manager.adapters.cli.base_controller import BaseCslController
from archive_manager.adapters.cli.contact_controller import ContactCslController

__all__ = ["BaseCslController", "ContactCslController"]
