#!/usr/bin/env python3
"""Tests for UI components and views.

These tests verify that UI components can be instantiated and
their basic functionality works correctly.
"""

from __future__ import annotations

from archive_manager.infrastructure.i18n import (
    ContactI18nMenus,
    ContactI18nTables,
    I18nMenu,
    I18nMenuOption,
    I18nMenus,
    I18nTable,
    I18nTables,
)


class TestI18nMenuOption:
    """Tests for I18nMenuOption dataclass."""

    def test_option_menu_creation(self) -> None:
        """Test I18nMenuOption can be created with id and text."""
        option = I18nMenuOption(id="test", text="Test Option")
        assert option.id == "test"
        assert option.text == "Test Option"


class TestI18nMenu:
    """Tests for I18nMenu class."""

    def test_menu_config_creation(self) -> None:
        """Test I18nMenu can be created with title and options."""
        options = [
            I18nMenuOption(id="opt1", text="Option 1"),
            I18nMenuOption(id="opt2", text="Option 2"),
        ]
        menu = I18nMenu(title="Test Menu", options=options)
        assert menu.title == "Test Menu"
        assert menu.num_options == 2

    def test_menu_config_get_option_id_valid(self) -> None:
        """Test get_option_id returns correct ID for valid index."""
        options = [
            I18nMenuOption(id="opt1", text="Option 1"),
            I18nMenuOption(id="opt2", text="Option 2"),
        ]
        menu = I18nMenu(title="Test Menu", options=options)
        assert menu.get_option_id(1) == "opt1"
        assert menu.get_option_id(2) == "opt2"

    def test_menu_config_get_option_id_invalid(self) -> None:
        """Test get_option_id returns None for invalid index."""
        options = [I18nMenuOption(id="opt1", text="Option 1")]
        menu = I18nMenu(title="Test Menu", options=options)
        assert menu.get_option_id(0) is None
        assert menu.get_option_id(2) is None

    def test_menu_config_add_option(self) -> None:
        """Test adding options to menu."""
        menu = I18nMenu(title="Test Menu", options=[])
        menu.add_option("new", "New Option")
        assert menu.num_options == 1
        assert menu.options[0].id == "new"

    def test_menu_config_clear_options(self) -> None:
        """Test clearing options from menu."""
        options = [I18nMenuOption(id="opt1", text="Option 1")]
        menu = I18nMenu(title="Test Menu", options=options)
        menu.clear_options()
        assert menu.num_options == 0


class TestI18nTable:
    """Tests for I18nTable class."""

    def test_table_config_creation(self) -> None:
        """Test I18nTable can be created with title and headers."""
        config = I18nTable(
            title="Test Table",
            headers={"name": "Name", "email": "Email"},
            footer="Total: {count}",
        )
        assert config.title == "Test Table"
        assert config.headers == {"name": "Name", "email": "Email"}
        assert config.footer == "Total: {count}"

    def test_table_config_build_table(self) -> None:
        """Test building a Rich table from config."""
        config = I18nTable(
            title="Contacts",
            headers={"first_name": "First Name", "email": "Email"},
        )
        data = [
            {"first_name": "Ana", "email": "ana@test.com"},
            {"first_name": "Bob", "email": "bob@test.com"},
        ]
        table = config.build_table(data)
        assert table is not None
        assert table.title == "Contacts"
        # Table should have 3 columns: #, First Name, Email
        assert len(table.columns) == 3


class TestContactI18nMenus:
    """Tests for ContactI18nMenus loader class."""

    def test_menus_loader_loads_from_json(self) -> None:
        """Test ContactI18nMenus loads menu definitions from JSON file."""
        # Clear cache to ensure fresh load
        I18nMenus.clear_cache()

        # Load a real menu from the test resources
        menu = ContactI18nMenus.contact_list_menu("en")

        # Verify menu was loaded with expected structure
        assert menu.title != ""
        assert len(menu.options) > 0
        assert all(opt.id for opt in menu.options)

    def test_pagination_menu_loader_loads_from_json(self) -> None:
        """Test ContactI18nMenus loads pagination menu definitions."""
        I18nMenus.clear_cache()
        menu = ContactI18nMenus.contact_pagination_menu("en")

        assert menu.title != ""
        assert len(menu.options) == 3
        assert {opt.id for opt in menu.options} == {"previous", "next", "return"}

    def test_loaded_menu_isolation_from_cache(self) -> None:
        """Test mutating a loaded menu does not affect later loads."""
        I18nMenus.clear_cache()

        menu = ContactI18nMenus.contact_pagination_menu("en")
        menu.clear_options()

        fresh_menu = ContactI18nMenus.contact_pagination_menu("en")
        assert len(fresh_menu.options) == 3
        assert {opt.id for opt in fresh_menu.options} == {
            "previous",
            "next",
            "return",
        }


class TestContactI18nTables:
    """Tests for ContactI18nTables loader class."""

    def test_tables_loader_loads_from_json(self) -> None:
        """Test ContactI18nTables loads table definitions from JSON file."""
        # Clear cache to ensure fresh load
        I18nTables.clear_cache()

        # Load a real table from the test resources
        table = ContactI18nTables.contact_table("en")

        # Verify table was loaded with expected structure
        assert table.headers is not None
        assert len(table.headers) > 0

    def test_loaded_table_isolation_from_cache(self) -> None:
        """Test mutating a loaded table does not affect later loads."""
        I18nTables.clear_cache()

        table = ContactI18nTables.contact_table("en")
        table.headers.clear()

        fresh_table = ContactI18nTables.contact_table("en")
        assert len(fresh_table.headers) > 0
