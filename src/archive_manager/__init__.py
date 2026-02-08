#!/usr/bin/env python3
"""Archive Manager — Contact Management Application.

A command-line application for managing contacts with SQLite storage
via SQLAlchemy, multilingual support (en/es), and Rich-based UI rendering.

Architecture: Clean Architecture (core → application → infrastructure → adapters).
"""

from archive_manager.cli import main

__all__ = ["main"]
