#!/usr/bin/env python3
"""Application entry point for the CLI adapter."""

from __future__ import annotations

import logging
import sys

from archive_manager.adapters.cli.contact_controller import ContactCslController
from archive_manager.adapters.cli.states.contact_states import (
    AppContext,
    BaseState,
    MainContactMenuState,
)
from archive_manager.adapters.cli.ui.contact_csl_ui import ContactCslUI
from archive_manager.application.services.contact_service import ContactService
from archive_manager.infrastructure.config import (
    DEFAULT_LANGUAGE,
    Session,
    Settings,
)
from archive_manager.infrastructure.i18n import (
    I18nMenus,
    I18nMessages,
    I18nTables,
)
from archive_manager.infrastructure.persistence import SqliteContactRepository
from archive_manager.infrastructure.persistence.db import SqliteConnection

logger = logging.getLogger(__name__)

# Type alias for contact context
ContactContext = AppContext[ContactCslUI, ContactCslController]


def create_context() -> ContactContext:
    """Create the application context with all dependencies.

    Wires all components via constructor injection. No global singletons.

    Returns:
        Configured AppContext with session, UI, and controller.
    """
    settings = Settings()

    # Configure i18n subsystem (class-level injection — called once)
    I18nMessages.configure(settings.i18n)
    I18nMenus.configure(settings.i18n)
    I18nTables.configure(settings.i18n)

    session = Session()
    session.language = (
        settings.i18n.language or settings.get_system_language() or DEFAULT_LANGUAGE
    )

    connection = SqliteConnection(settings.database)
    repo = SqliteContactRepository(connection)
    service = ContactService(repo)
    controller = ContactCslController(service)
    ui = ContactCslUI()

    return AppContext(session, ui, controller)


def run(ctx: ContactContext) -> None:
    """Run the state machine loop.

    Args:
        ctx: Application context with session, UI, and controller.
    """
    state: BaseState | None = MainContactMenuState()

    while state is not None:
        state = state.run(ctx)


def main() -> None:
    """Initialize and run the console application."""
    try:
        ctx = create_context()
        run(ctx)

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)

    except Exception as exc:
        logger.critical(
            "Fatal error during application startup: %s - %s",
            type(exc).__name__,
            str(exc),
            exc_info=True,
        )
        print(f"\nFatal error: {exc}", file=sys.stderr)
        sys.exit(1)
