#!/usr/bin/env python3
"""Unit tests for state machine and handle_errors decorator.

Tests cover:
- State base class
- handle_errors decorator behavior with different exception types
- Retry logic for validation errors and warnings
- Abort logic for errors and exceptions
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from archive_manager.adapters.cli.states import AppContext, BaseState
from archive_manager.core.errors import (
    AppError,
    AppException,
    AppValidationErrors,
    AppWarning,
)

# ==============================================================================
# Test Fixtures
# ==============================================================================


@pytest.fixture
def mock_ui():
    """Create mock UI with common methods."""
    ui = MagicMock()
    ui.print_errors = MagicMock()
    ui.print_warning = MagicMock()
    ui.print_error = MagicMock()
    ui.pause = MagicMock()
    return ui


@pytest.fixture
def mock_session():
    """Create mock session with language."""
    session = MagicMock()
    session.language = "en"
    return session


@pytest.fixture
def mock_service():
    """Create mock service."""
    return MagicMock()


@pytest.fixture
def mock_context(mock_session, mock_ui, mock_service):
    """Create mock application context."""
    return AppContext(session=mock_session, ui=mock_ui, service=mock_service)


# ==============================================================================
# Test State Classes
# ==============================================================================


class ConcreteState(BaseState):
    """Concrete implementation of BaseState for testing."""

    def __init__(self):
        """Initialize test state with error simulation parameters."""
        self.call_count = 0
        self.should_raise: BaseException | None = None
        self.raise_times: int = 0

    def run(self, ctx: AppContext) -> BaseState | None:
        """Simple run method for testing."""
        return None

    @BaseState.handle_errors
    def action_with_errors(self, ctx: AppContext) -> str:
        """Action that may raise errors for testing handle_errors."""
        self.call_count += 1

        if self.should_raise and self.call_count <= self.raise_times:
            raise self.should_raise

        return "success"


# ==============================================================================
# Basic State Tests
# ==============================================================================


class TestStateBasic:
    """Tests for basic State functionality."""

    def test_state_is_abstract(self):
        """BaseState cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseState()  # type: ignore

    def test_state_subclass_can_be_instantiated(self):
        """BaseState subclass with run method can be instantiated."""
        state = ConcreteState()
        assert state is not None

    def test_format_app_issue_with_code_and_origin(self):
        """Format app issue includes code and origin."""
        issue = AppError("TEST_ERROR", origin="TestService.method")
        result = BaseState._format_app_issue(issue)

        assert "TestService.method" in result
        assert "TEST_ERROR" in result


# ==============================================================================
# Handle Errors Decorator Tests
# ==============================================================================


class TestHandleErrorsDecorator:
    """Tests for the @handle_errors decorator."""

    def test_successful_execution(self, mock_context):
        """Successful execution returns result without UI interaction."""
        state = ConcreteState()

        result = state.action_with_errors(mock_context)

        assert result == "success"
        assert state.call_count == 1
        mock_context.ui.print_errors.assert_not_called()
        mock_context.ui.print_error.assert_not_called()

    def test_validation_errors_retry_once_then_succeed(self, mock_context):
        """Validation errors show errors and retry."""
        state = ConcreteState()
        errors = [AppError(code="TEST_ERROR", origin="test", field="test")]
        state.should_raise = AppValidationErrors(errors, origin="test")
        state.raise_times = 1  # Fail first time, succeed second

        result = state.action_with_errors(mock_context)

        assert result == "success"
        assert state.call_count == 2  # Failed once, succeeded on retry
        mock_context.ui.print_errors.assert_called_once()
        mock_context.ui.pause.assert_called()

    def test_validation_errors_retry_multiple_times(self, mock_context):
        """Validation errors retry until success."""
        state = ConcreteState()
        errors = [AppError(code="TEST_ERROR", origin="test", field="test")]
        state.should_raise = AppValidationErrors(errors, origin="test")
        state.raise_times = 3  # Fail 3 times, succeed on 4th

        result = state.action_with_errors(mock_context)

        assert result == "success"
        assert state.call_count == 4
        assert mock_context.ui.print_errors.call_count == 3

    def test_warning_retries_then_succeeds(self, mock_context):
        """Warnings show warning and retry."""
        state = ConcreteState()
        state.should_raise = AppWarning(
            "TEST_WARNING", origin="test", search_field="name"
        )
        state.raise_times = 1

        result = state.action_with_errors(mock_context)

        assert result == "success"
        assert state.call_count == 2
        mock_context.ui.print_warning.assert_called_once()

    def test_app_error_aborts_operation(self, mock_context):
        """AppError shows error and returns None (abort)."""
        state = ConcreteState()
        state.should_raise = AppError("TEST_ERROR", origin="test")
        state.raise_times = 999  # Always raise

        result = state.action_with_errors(mock_context)

        assert result is None  # Aborted
        assert state.call_count == 1  # No retry
        mock_context.ui.print_error.assert_called_once()

    def test_app_exception_aborts_with_generic_error(self, mock_context):
        """AppException shows generic error and aborts."""
        state = ConcreteState()
        state.should_raise = AppException("DB_ERROR", origin="test")
        state.raise_times = 999

        with patch("archive_manager.adapters.cli.states.base_state.logger"):
            result = state.action_with_errors(mock_context)

        assert result is None
        assert state.call_count == 1
        mock_context.ui.print_error.assert_called_once_with("en", "UNKNOWN_ERROR")

    def test_unhandled_exception_aborts_with_generic_error(self, mock_context):
        """Unhandled exceptions show generic error and abort."""
        state = ConcreteState()
        state.should_raise = RuntimeError("Unexpected error")
        state.raise_times = 999

        with patch("archive_manager.adapters.cli.states.base_state.logger"):
            result = state.action_with_errors(mock_context)

        assert result is None
        assert state.call_count == 1
        mock_context.ui.print_error.assert_called_once_with("en", "UNKNOWN_ERROR")

    def test_keyboard_interrupt_propagates(self, mock_context):
        """KeyboardInterrupt is not caught."""
        state = ConcreteState()
        state.should_raise = KeyboardInterrupt()
        state.raise_times = 999

        with pytest.raises(KeyboardInterrupt):
            state.action_with_errors(mock_context)

    def test_system_exit_propagates(self, mock_context):
        """SystemExit is not caught."""
        state = ConcreteState()
        state.should_raise = SystemExit(0)
        state.raise_times = 999

        with pytest.raises(SystemExit):
            state.action_with_errors(mock_context)


# ==============================================================================
# Integration-style State Flow Tests
# ==============================================================================


class TestStateFlow:
    """Tests for state machine flow patterns."""

    def test_state_returns_next_state(self, mock_context):
        """State can return next state for transition."""

        @dataclass
        class NextState(BaseState):
            def run(self, ctx) -> BaseState | None:
                return None

        class InitialState(BaseState):
            def run(self, ctx) -> BaseState | None:
                return NextState()

        state = InitialState()
        next_state = state.run(mock_context)

        assert isinstance(next_state, NextState)

    def test_state_returns_none_to_exit(self, mock_context):
        """State returning None signals exit."""

        class ExitState(BaseState):
            def run(self, ctx) -> BaseState | None:
                return None

        state = ExitState()
        result = state.run(mock_context)

        assert result is None

    def test_state_returns_self_for_loop(self, mock_context):
        """State returning self continues on same state."""

        class LoopState(BaseState):
            def __init__(self):
                self.iterations = 0

            def run(self, ctx) -> BaseState | None:
                self.iterations += 1
                if self.iterations < 3:
                    return self
                return None

        state = LoopState()

        # Simulate state machine loop
        current: BaseState | None = state
        while current is not None:
            current = current.run(mock_context)

        assert state.iterations == 3
