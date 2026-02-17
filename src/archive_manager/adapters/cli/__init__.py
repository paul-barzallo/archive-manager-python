#!/usr/bin/env python3
"""CLI adapter layer — console-based delivery mechanism."""

from archive_manager.adapters.cli.main import create_context, main, run

__all__ = [
    "create_context",
    "main",
    "run",
]
