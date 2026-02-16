#!/usr/bin/env python3
"""API adapter layer — HTTP delivery mechanism."""

from archive_manager.adapters.api.main import create_app, run

__all__ = ["create_app", "run"]
