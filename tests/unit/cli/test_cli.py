#!/usr/bin/env python3
"""Unit tests for CLI components instantiation.

Tests verify that all CLI components can be correctly instantiated
and wired together, catching configuration errors early.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from archive_manager.adapters.cli import ContactCslController
from archive_manager.adapters.cli.states import (
    AppContext,
    BaseState,
    MainContactMenuState,
)
from archive_manager.adapters.cli.ui import ContactCslUI
from archive_manager.cli import create_context, run
from archive_manager.infrastructure.config import (
    DEFAULT_LANGUAGE,
    Session,
    Settings,
)


class TestCreateContext:
    """Tests for context creation factory."""

    def test_create_context_returns_app_context(self) -> None:
        """Verify `create_context()` returns an AppContext instance."""
        ctx = create_context()

        assert isinstance(ctx, AppContext)

    def test_create_context_has_session(self) -> None:
        """Verify context has a Session instance."""
        ctx = create_context()

        assert isinstance(ctx.session, Session)

    def test_create_context_session_has_language(self) -> None:
        """Verify session has a language configured."""
        ctx = create_context()

        assert ctx.session.language is not None
        assert ctx.session.language in ("en", "es")

    def test_create_context_has_ui(self) -> None:
        """Verify context has a ContactCslUI instance."""
        ctx = create_context()

        assert isinstance(ctx.ui, ContactCslUI)

    def test_create_context_has_controller(self) -> None:
        """Verify context has a ContactCslController instance."""
        ctx = create_context()

        assert isinstance(ctx.controller, ContactCslController)


class TestRun:
    """Tests for the run function."""

    def test_run_creates_initial_state(self) -> None:
        """Verify `run()` creates MainContactMenuState."""
        ctx = create_context()

        with patch.object(MainContactMenuState, "run", return_value=None) as mock_run:
            run(ctx)

            mock_run.assert_called_once_with(ctx)

    def test_run_loops_until_none(self) -> None:
        """Verify `run()` continues until state returns `None`."""
        ctx = create_context()

        mock_state1 = MagicMock()
        mock_state2 = MagicMock()
        mock_state2.run.return_value = None
        mock_state1.run.return_value = mock_state2

        with patch(
            "archive_manager.cli.MainContactMenuState",
            return_value=mock_state1,
        ):
            run(ctx)

        mock_state1.run.assert_called_once_with(ctx)
        mock_state2.run.assert_called_once_with(ctx)


class TestSession:
    """Tests for Session component."""

    def test_session_instantiation(self) -> None:
        """Verify Session can be instantiated with defaults."""
        session = Session()

        assert session is not None
        assert isinstance(session.language, str)
        assert len(session.language) > 0

    def test_session_language_assignment(self) -> None:
        """Verify language can be assigned to session."""
        session = Session()

        session.language = DEFAULT_LANGUAGE

        assert session.language == DEFAULT_LANGUAGE

    def test_session_set_language_valid(self) -> None:
        """Verify `set_language()` with valid language."""
        session = Session()
        settings = Settings.for_testing()

        result = session.set_language(DEFAULT_LANGUAGE, settings.i18n)

        assert result is True
        assert session.language == DEFAULT_LANGUAGE

    def test_session_set_language_invalid(self) -> None:
        """Verify `set_language()` rejects invalid language."""
        session = Session()
        settings = Settings.for_testing()

        result = session.set_language("invalid_lang_xyz", settings.i18n)

        assert result is False


class TestAppContext:
    """Tests for AppContext component."""

    def test_app_context_instantiation(self) -> None:
        """Verify AppContext can be instantiated with components."""
        session = Session()
        ui = MagicMock(spec=ContactCslUI)
        controller = MagicMock(spec=ContactCslController)

        ctx = AppContext(session, ui, controller)

        assert ctx.session is session
        assert ctx.ui is ui
        assert ctx.controller is controller


class TestCLIComponents:
    """Test CLI component instantiation."""

    def test_contacts_csl_ui_instantiation(self) -> None:
        """Verify ContactCslUI can be instantiated."""
        ui = ContactCslUI()

        assert ui is not None

    def test_main_contacts_menu_state_instantiation(self) -> None:
        """Verify MainContactMenuState can be instantiated."""
        state = MainContactMenuState()

        assert state is not None
        assert isinstance(state, BaseState)


class TestCLIMain:
    """Test CLI main function behavior."""

    @patch("archive_manager.cli.create_context")
    @patch("archive_manager.cli.run")
    def test_main_calls_create_context_and_run(
        self,
        mock_run: MagicMock,
        mock_create_context: MagicMock,
    ) -> None:
        """Verify main() calls `create_context()` and `run()`."""
        from archive_manager.cli import main

        mock_ctx = MagicMock()
        mock_create_context.return_value = mock_ctx

        main()

        mock_create_context.assert_called_once()
        mock_run.assert_called_once_with(mock_ctx)

    @patch("archive_manager.cli.create_context")
    def test_main_keyboard_interrupt(
        self,
        mock_create_context: MagicMock,
    ) -> None:
        """Verify main() handles KeyboardInterrupt gracefully."""
        from archive_manager.cli import main

        mock_create_context.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
