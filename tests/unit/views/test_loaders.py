#!/usr/bin/env python3
"""Tests for i18n data loaders.

Verifies:
- Loading of menu/table/message data from JSON
- Caching mechanisms
- Error handling (files not found, invalid JSON)
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from archive_manager.infrastructure.i18n.loaders import (
    I18nMenusLoader,
    I18nMessageLoader,
    I18nTablesLoader,
    _I18nBaseLoader,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear loader cache before each test."""
    _I18nBaseLoader.clear_cache()
    yield
    _I18nBaseLoader.clear_cache()


class TestI18nLoaders:
    """Tests for base loading logic and specific implementations."""

    def test_load_menu_success(self):
        """Test successful menu loading."""
        data = {"main_menu": {"title": "Main", "options": []}}
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(data))):
            result = I18nMenusLoader.get_i18nmenu(Path("menus.json"), "main_menu")
            assert result == data["main_menu"]

    def test_load_menu_not_found_file(self):
        """Test loading menu from non-existent file returns None."""
        with patch("pathlib.Path.open", side_effect=FileNotFoundError):
            result = I18nMenusLoader.get_i18nmenu(Path("missing.json"), "main_menu")
            assert result is None

    def test_load_menu_key_not_found(self):
        """Test loading non-existent menu key returns None."""
        data = {"other_menu": {}}
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(data))):
            result = I18nMenusLoader.get_i18nmenu(Path("menus.json"), "main_menu")
            assert result is None

    def test_load_menu_invalid_json(self):
        """Test loading invalid JSON returns None."""
        with patch("pathlib.Path.open", mock_open(read_data="{invalid_json")):
            result = I18nMenusLoader.get_i18nmenu(Path("menus.json"), "main_menu")
            assert result is None

    def test_load_menu_invalid_structure(self):
        """Test menu data that is not a dictionary."""
        data = {"main_menu": "not a dict"}
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(data))):
            result = I18nMenusLoader.get_i18nmenu(Path("menus.json"), "main_menu")
            assert result is None

    def test_caching_behavior(self):
        """Test that data is cached and file is read only once."""
        data = {"menu": {}}
        mock_file = mock_open(read_data=json.dumps(data))
        path = Path("cached.json")

        with patch("pathlib.Path.open", mock_file):
            # First load
            I18nMenusLoader.get_i18nmenu(path, "menu")
            # Second load
            I18nMenusLoader.get_i18nmenu(path, "menu")

        # File should be opened only once
        mock_file.assert_called_once()


class TestSpecificLoaders:
    """Test functionality specific to Tables and Messages loaders."""

    def test_load_table_success(self):
        """Test successful table loading."""
        data = {"contacts": {"title": "List", "headers": {}}}
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(data))):
            result = I18nTablesLoader.get_i18ntable(Path("tables.json"), "contacts")
            assert result == data["contacts"]

    def test_load_message_success(self):
        """Test successful message loading."""
        data = {"welcome": {"message": "Hello"}}
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(data))):
            result = I18nMessageLoader.get_i18nmessage(Path("messages.json"), "welcome")
            assert result == data["welcome"]

    def test_load_message_key_not_found(self):
        """Test message loading fails properly for missing key."""
        data = {"bye": {}}
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(data))):
            result = I18nMessageLoader.get_i18nmessage(Path("messages.json"), "welcome")
            assert result is None
