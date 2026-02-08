#!/usr/bin/env python3
"""State machine base and generic application context for console controllers.

Provides ``BaseState`` (abstract state), ``AppContext`` (generic context
dataclass), and the ``handle_errors`` decorator for centralised domain
error handling.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from decorator import decorator

from archive_manager.core.errors import (
    AppError,
    AppException,
    AppInfrastructureError,
    AppValidationErrors,
    AppWarning,
)

if TYPE_CHECKING:
    from archive_manager.adapters.cli import BaseCslController
    from archive_manager.adapters.cli.ui import CslUI
    from archive_manager.infrastructure.config import Session

logger = logging.getLogger(__name__)

# Type variables for generic context
U = TypeVar("U", bound="CslUI")
C = TypeVar("C", bound="BaseCslController")
T = TypeVar("T")


@dataclass
class AppContext(Generic[U, C]):
    """Generic application context holding session, UI and controller.

    Type parameters allow subclasses to specify concrete UI and Controller types
    for type-safe access without casts.

    Attributes:
        session: User session with language configuration.
        ui: Console UI instance for user interaction.
        controller: Controller instance for business logic.
    """

    session: Session
    ui: U
    controller: C


# --- State machine base ---
class BaseState(ABC):
    """Abstract base class for state machine states.

    Each state represents a step in the UI flow and returns the next state.
    """

    @abstractmethod
    def run(self, ctx: AppContext) -> BaseState | None:
        """Execute a UI step and return the next state."""
        ...

    @staticmethod
    def _format_app_issue(issue: AppException) -> str:
        """Format an application exception into a human-readable string."""
        parts = [f"{issue.origin}: {issue.code}"]
        if issue.field:
            parts.append(f"field={issue.field}")
        if issue.context:
            parts.append(f"context={issue.context}")
        return ", ".join(parts)

    @decorator
    @staticmethod
    def handle_errors(
        func: Callable[..., T], self: Any, ctx: Any, *args: Any, **kwargs: Any
    ) -> T | None:
        """Decorator to centralize domain error handling for controller actions.

        Error handling hierarchy (least to most severe):
        1. AppValidationErrors: Show all errors, allow retry
        2. AppWarning: Show warning, allow retry
        3. AppError: Show error, abort operation (return to previous state)
        4. AppException: Log details, show generic error, abort operation
        5. Exception: Log critical, show generic error, abort operation

        Extracts UI and language from AppContext (first argument after self)
        for error display.
        """
        ui = ctx.ui
        lang = ctx.session.language

        while True:
            try:
                return func(self, ctx, *args, **kwargs)

            except (KeyboardInterrupt, SystemExit):
                raise

            except AppValidationErrors as ve:
                # Validation errors: show all errors and retry the same operation
                logger.info(
                    "Validation errors in %s: %s",
                    ve.origin,
                    [err.code for err in ve.errors],
                )
                error_messages = [{err.code: err.context} for err in ve.errors]
                ui.print_errors(lang, error_messages)
                ui.pause(lang)
                # Continue loop to retry
                continue

            except AppWarning as w:
                # Warnings: log, show warning, allow retry
                msg = BaseState._format_app_issue(w)
                logger.warning("AppWarning: %s", msg)
                ui.print_warning(lang, w.code, **w.context)
                ui.pause(lang)
                # Continue loop to retry
                continue

            except AppError as e:
                # Business errors: log, show specific error, abort operation
                msg = BaseState._format_app_issue(e)
                logger.warning("AppError (business): %s", msg)
                ui.print_error(lang, e.code, **e.context)
                ui.pause(lang)
                # Abort - return None to go back
                return None

            except AppInfrastructureError as exc:
                # Infrastructure errors: log full details, show generic message
                logger.exception(
                    "AppInfrastructureError: code=%s, origin=%s, context=%s",
                    exc.code,
                    exc.origin,
                    exc.context,
                )
                ui.print_error(lang, "UNKNOWN_ERROR")
                ui.pause(lang)
                return None

            except AppException as exc:
                # Generic app errors: log full details, show generic message to user
                logger.exception(
                    "AppException: code=%s, origin=%s, context=%s",
                    exc.code,
                    exc.origin,
                    exc.context,
                )
                ui.print_error(lang, "UNKNOWN_ERROR")
                ui.pause(lang)
                return None

            except Exception as exc:
                # Critical unhandled errors: log everything, show generic message
                logger.critical(
                    "Unhandled exception: %s - %s",
                    type(exc).__name__,
                    str(exc),
                    exc_info=True,
                )
                ui.print_error(lang, "UNKNOWN_ERROR")
                ui.pause(lang)
                return None
