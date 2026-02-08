#!/usr/bin/env python3
"""Unit tests for CslUI and ContactCslUI classes.

Tests cover:
- Basic UI rendering methods
- Error, warning, and success message display
- Menu and table display
- Input prompts and confirmations
- Mocking of Rich Console and InquirerPy
"""

from __future__ import annotations

from collections.abc import Sequence
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from archive_manager.adapters.cli.ui import ContactCslUI, CslUI
from archive_manager.application.dto import ContactDTO

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_console() -> MagicMock:
    """Create a mock Rich Console."""
    return MagicMock(spec=Console)


@pytest.fixture
def csl_ui(mock_console: MagicMock) -> CslUI:
    """Create CslUI instance with mocked console."""
    return CslUI(console=mock_console)


@pytest.fixture
def contacts_ui(mock_console: MagicMock) -> ContactCslUI:
    """Create ContactCslUI instance with mocked console."""
    return ContactCslUI(console=mock_console)


@pytest.fixture
def sample_contacts() -> Sequence[ContactDTO]:
    """Create sample contacts for testing."""
    return [
        ContactDTO(1, "john", "doe", "john@example.com", "1234567890"),
        ContactDTO(2, "jane", "smith", "jane@example.com", "0987654321"),
    ]


# ==============================================================================
# CslUI Base Class Tests
# ==============================================================================


class TestCslUIBasic:
    """Tests for basic CslUI functionality."""

    def test_csl_ui_instantiation(self) -> None:
        """Test CslUI can be instantiated."""
        ui = CslUI()
        assert ui is not None
        assert ui._console is not None

    def test_csl_ui_with_custom_console(self, mock_console: MagicMock) -> None:
        """Test CslUI can be instantiated with custom console."""
        ui = CslUI(console=mock_console)
        assert ui._console is mock_console

    @patch("archive_manager.adapters.cli.ui.csl_ui.os.system")
    def test_clear_screen(self, mock_system: MagicMock, csl_ui: CslUI) -> None:
        """Test clear_screen calls os.system."""
        csl_ui.clear_screen()
        mock_system.assert_called_once()

    def test_show_title(self, csl_ui: CslUI, mock_console: MagicMock) -> None:
        """Test show_title renders title panel."""
        with patch.object(csl_ui, "clear_screen"):
            csl_ui.show_title()
        # Verify console.print was called (for the title panel)
        assert mock_console.print.called


class TestCslUIMessages:
    """Tests for CslUI message display methods."""

    def test_print_error(self, csl_ui: CslUI, mock_console: MagicMock) -> None:
        """Test print_error displays error panel."""
        csl_ui.print_error("en", "UNKNOWN_ERROR")
        # Should call print at least twice (newline + panel)
        assert mock_console.print.call_count >= 1

    def test_print_error_with_details(
        self, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test print_error with additional details."""
        csl_ui.print_error("en", "UNKNOWN_ERROR", details="Extra info")
        assert mock_console.print.call_count >= 1

    def test_print_warning(self, csl_ui: CslUI, mock_console: MagicMock) -> None:
        """Test print_warning displays warning panel."""
        csl_ui.print_warning("en", "CONTACT_NOT_FOUND", name="test")
        assert mock_console.print.call_count >= 1

    def test_print_success(self, csl_ui: CslUI, mock_console: MagicMock) -> None:
        """Test print_success displays success panel."""
        csl_ui.print_success("en", "SUCCESS_CONTACT_CREATED")
        assert mock_console.print.call_count >= 1

    def test_print_info(self, csl_ui: CslUI, mock_console: MagicMock) -> None:
        """Test print_info displays info panel."""
        csl_ui.print_info("en", "INFO_OPERATION_CANCELLED")
        assert mock_console.print.call_count >= 1

    def test_print_errors_multiple(
        self, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test print_errors with multiple error codes."""
        errors = [
            {"FIRST_NAME_REQUIRED": {}},
            {"EMAIL_REQUIRED": {}},
        ]
        csl_ui.print_errors("en", errors)
        assert mock_console.print.call_count >= 1


class TestCslUIInput:
    """Tests for CslUI input methods."""

    @patch("archive_manager.adapters.cli.ui.csl_ui.InputPrompt")
    def test_get_input(
        self, mock_input_prompt: MagicMock, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test get_input prompts user and returns stripped input."""
        mock_instance = MagicMock()
        mock_instance.execute.return_value = "  test value  "
        mock_input_prompt.return_value = mock_instance

        result = csl_ui.get_input("en", "PROMPT_FIRST_NAME")

        assert result == "test value"
        mock_input_prompt.assert_called_once()

    @patch("archive_manager.adapters.cli.ui.csl_ui.InputPrompt")
    def test_get_input_with_default(
        self, mock_input_prompt: MagicMock, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test get_input with default value."""
        mock_instance = MagicMock()
        mock_instance.execute.return_value = ""
        mock_input_prompt.return_value = mock_instance

        result = csl_ui.get_input("en", "PROMPT_FIRST_NAME", default="default")

        assert result == ""
        # Verify default was passed to InputPrompt
        call_kwargs = mock_input_prompt.call_args[1]
        assert call_kwargs["default"] == "default"

    @patch("archive_manager.adapters.cli.ui.csl_ui.InputPrompt")
    def test_get_input_handles_none(
        self, mock_input_prompt: MagicMock, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test get_input handles None return value."""
        mock_instance = MagicMock()
        mock_instance.execute.return_value = None
        mock_input_prompt.return_value = mock_instance

        result = csl_ui.get_input("en", "PROMPT_FIRST_NAME")

        assert result == ""

    @patch("archive_manager.adapters.cli.ui.csl_ui.ListPrompt")
    def test_confirm_yes(
        self, mock_list_prompt: MagicMock, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test confirm returns True when user confirms."""
        mock_instance = MagicMock()
        mock_instance.execute.return_value = True
        mock_list_prompt.return_value = mock_instance

        result = csl_ui.confirm("en", "CONFIRM_DELETE_CONTACT")

        assert result is True

    @patch("archive_manager.adapters.cli.ui.csl_ui.ListPrompt")
    def test_confirm_no(
        self, mock_list_prompt: MagicMock, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test confirm returns False when user declines."""
        mock_instance = MagicMock()
        mock_instance.execute.return_value = False
        mock_list_prompt.return_value = mock_instance

        result = csl_ui.confirm("en", "CONFIRM_DELETE_CONTACT")

        assert result is False

    @patch("archive_manager.adapters.cli.ui.csl_ui.Prompt.ask")
    def test_pause(
        self, mock_ask: MagicMock, csl_ui: CslUI, mock_console: MagicMock
    ) -> None:
        """Test pause waits for user input."""
        csl_ui.pause("en")
        mock_ask.assert_called_once()


# ==============================================================================
# ContactCslUI Tests
# ==============================================================================


class TestContactCslUIMenus:
    """Tests for ContactCslUI menu methods."""

    @patch.object(ContactCslUI, "_show_menu")
    def test_show_contact_list_menu(
        self, mock_show_menu: MagicMock, contacts_ui: ContactCslUI
    ) -> None:
        """Test show_contact_list_menu calls _show_menu."""
        mock_show_menu.return_value = "add"
        result = contacts_ui.show_contact_list_menu("en")
        assert result == "add"
        mock_show_menu.assert_called_once()

    @patch.object(ContactCslUI, "_show_menu")
    def test_show_contact_menu(
        self, mock_show_menu: MagicMock, contacts_ui: ContactCslUI
    ) -> None:
        """Test show_contact_menu calls _show_menu."""
        mock_show_menu.return_value = "view"
        result = contacts_ui.show_contact_menu("en")
        assert result == "view"
        mock_show_menu.assert_called_once()

    @patch.object(ContactCslUI, "_show_menu")
    def test_show_find_contact_menu(
        self, mock_show_menu: MagicMock, contacts_ui: ContactCslUI
    ) -> None:
        """Test show_find_contact_menu calls _show_menu."""
        mock_show_menu.return_value = "full_name"
        result = contacts_ui.show_find_contact_menu("en")
        assert result == "full_name"
        mock_show_menu.assert_called_once()


class TestContactCslUITables:
    """Tests for ContactCslUI table display methods."""

    @patch.object(ContactCslUI, "_show_table")
    def test_show_contacts_table(
        self,
        mock_show_table: MagicMock,
        contacts_ui: ContactCslUI,
        sample_contacts: Sequence[ContactDTO],
    ) -> None:
        """Test show_contacts_table calls _show_table."""
        contacts_ui.show_contacts_table("en", sample_contacts)
        mock_show_table.assert_called_once()


class TestContactCslUIDetails:
    """Tests for ContactCslUI detail display methods."""

    @patch.object(ContactCslUI, "_show_details")
    def test_show_contact_detail(
        self, mock_show_details: MagicMock, contacts_ui: ContactCslUI
    ) -> None:
        """Test show_contact_detail calls _show_details."""
        contact = ContactDTO(1, "john", "doe", "john@example.com", "1234567890")
        contacts_ui.show_contact_detail("en", contact)
        mock_show_details.assert_called_once()

    def test_get_contact_fields(self, contacts_ui: ContactCslUI) -> None:
        """Test _get_contact_fields returns correct field structure."""
        contact = ContactDTO(1, "john", "doe", "john@example.com", "1234567890")
        fields = contacts_ui._get_contact_fields("en", contact)

        assert len(fields) == 4
        assert all("text" in field and "value" in field for field in fields)
        assert fields[0]["value"] == "john"
        assert fields[1]["value"] == "doe"
        assert fields[2]["value"] == "john@example.com"
        assert fields[3]["value"] == "1234567890"


class TestContactCslUISelectMenu:
    """Tests for ContactCslUI select contact menu."""

    @patch.object(ContactCslUI, "_show_menu")
    def test_show_select_contact_menu(
        self,
        mock_show_menu: MagicMock,
        contacts_ui: ContactCslUI,
        sample_contacts: Sequence[ContactDTO],
    ) -> None:
        """Test show_select_contact_menu with contacts."""
        mock_show_menu.return_value = "0"
        result = contacts_ui.show_select_contact_menu("en", sample_contacts)
        assert result == "0"
        mock_show_menu.assert_called_once()

    @patch.object(ContactCslUI, "_show_menu")
    def test_show_select_contact_menu_return(
        self,
        mock_show_menu: MagicMock,
        contacts_ui: ContactCslUI,
        sample_contacts: Sequence[ContactDTO],
    ) -> None:
        """Test show_select_contact_menu returns 'return' option."""
        mock_show_menu.return_value = "return"
        result = contacts_ui.show_select_contact_menu("en", sample_contacts)
        assert result == "return"


# ==============================================================================
# Integration-like Tests (with real i18n)
# ==============================================================================


class TestCslUIWithRealI18n:
    """Tests that verify UI methods work with real i18n system."""

    def test_print_error_with_real_i18n(self, mock_console: MagicMock) -> None:
        """Test that error messages are loaded from i18n."""
        ui = CslUI(console=mock_console)
        # Should not raise any exceptions
        ui.print_error("en", "UNKNOWN_ERROR")
        assert mock_console.print.called

    def test_print_warning_with_real_i18n(self, mock_console: MagicMock) -> None:
        """Test that warning messages are loaded from i18n."""
        ui = ContactCslUI(console=mock_console)
        # Should not raise any exceptions
        ui.print_warning("en", "CONTACT_NOT_FOUND", name="test")
        assert mock_console.print.called

    def test_print_success_with_real_i18n(self, mock_console: MagicMock) -> None:
        """Test that success messages are loaded from i18n."""
        ui = ContactCslUI(console=mock_console)
        # Should not raise any exceptions
        ui.print_success("en", "SUCCESS_CONTACT_CREATED")
        assert mock_console.print.called

    def test_cancel_shows_info(self, mock_console: MagicMock) -> None:
        """Test cancel method shows cancellation info."""
        ui = CslUI(console=mock_console)
        ui.cancel("en")
        assert mock_console.print.called


class TestCslUILanguageSupport:
    """Tests for language support in UI."""

    def test_print_error_spanish(self, mock_console: MagicMock) -> None:
        """Test error message in Spanish."""
        ui = CslUI(console=mock_console)
        ui.print_error("es", "UNKNOWN_ERROR")
        assert mock_console.print.called

    def test_print_success_spanish(self, mock_console: MagicMock) -> None:
        """Test success message in Spanish."""
        ui = ContactCslUI(console=mock_console)
        ui.print_success("es", "SUCCESS_CONTACT_CREATED")
        assert mock_console.print.called
