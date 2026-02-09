#!/usr/bin/env python3
"""Tests to verify all module imports and dependencies are correctly configured.

These tests ensure that all packages and their dependencies can be imported
without errors, catching missing dependencies or circular import issues early.
"""

from __future__ import annotations


class TestCoreImports:
    """Test core application imports."""

    def test_main_package_import(self) -> None:
        """Test main package can be imported."""
        from archive_manager import main

        assert callable(main)

    def test_cli_import(self) -> None:
        """Test CLI module can be imported."""
        from archive_manager.cli import main

        assert callable(main)


class TestDomainImports:
    """Test core domain layer imports."""

    def test_entities_import(self) -> None:
        """Test entities module exports."""
        from archive_manager.core.entities import Contact

        assert Contact is not None

    def test_validators_import(self) -> None:
        """Test validators subpackage exports."""
        from archive_manager.core.entities.validators import ContactValidator

        assert ContactValidator is not None

    def test_errors_import(self) -> None:
        """Test errors module exports."""
        from archive_manager.core.errors import (
            AppError,
            AppException,
            AppValidationErrors,
            AppWarning,
        )

        assert issubclass(AppException, Exception)
        assert issubclass(AppError, AppException)
        assert issubclass(AppWarning, AppException)
        assert issubclass(AppValidationErrors, Exception)

    def test_interfaces_import(self) -> None:
        """Test interface (protocol) exports."""
        from archive_manager.core.interfaces import (
            ContactRepository,
            Controller,
            DBConnection,
            Repository,
            Service,
        )

        assert Controller is not None
        assert ContactRepository is not None
        assert DBConnection is not None
        assert Repository is not None
        assert Service is not None


class TestApplicationImports:
    """Test application layer imports."""

    def test_services_import(self) -> None:
        """Test services module exports."""
        from archive_manager.application.services import (
            ContactPolicy,
            ContactService,
        )

        assert ContactPolicy is not None
        assert ContactService is not None

    def test_dto_import(self) -> None:
        """Test DTO module exports."""
        from archive_manager.application.dto import ContactDTO, ContactPageDTO

        assert ContactDTO is not None
        assert ContactPageDTO is not None


class TestInfrastructureImports:
    """Test infrastructure layer imports."""

    def test_persistence_import(self) -> None:
        """Test persistence module exports."""
        from archive_manager.infrastructure.persistence import (
            SqliteContactRepository,
        )

        assert SqliteContactRepository is not None

    def test_persistence_db_import(self) -> None:
        """Test database layer exports."""
        from archive_manager.infrastructure.persistence.db import (
            ContactORM,
            SqliteConnection,
        )

        assert ContactORM is not None
        assert SqliteConnection is not None

    def test_persistence_mappers_import(self) -> None:
        """Test mappers module exports."""
        from archive_manager.infrastructure.persistence.mappers import ContactMapper

        assert ContactMapper is not None

    def test_config_import(self) -> None:
        """Test config module exports."""
        from archive_manager.infrastructure.config import (
            DEFAULT_LANGUAGE,
            Session,
            Settings,
        )

        assert DEFAULT_LANGUAGE is not None
        assert Session is not None
        assert Settings is not None


class TestI18nImports:
    """Test i18n infrastructure imports."""

    def test_i18n_messages_import(self) -> None:
        """Test messages module exports via i18n package."""
        from archive_manager.infrastructure.i18n import I18nMessages

        assert I18nMessages is not None

    def test_i18n_menus_import(self) -> None:
        """Test menus module components via i18n package."""
        from archive_manager.infrastructure.i18n import (
            I18nMenu,
            I18nMenuOption,
            I18nMenus,
        )

        assert I18nMenu is not None
        assert I18nMenus is not None
        assert I18nMenuOption is not None

    def test_i18n_tables_import(self) -> None:
        """Test tables module components via i18n package."""
        from archive_manager.infrastructure.i18n import I18nTable, I18nTables

        assert I18nTable is not None
        assert I18nTables is not None

    def test_i18n_loader_classes_import(self) -> None:
        """Test i18n loader classes."""
        from archive_manager.infrastructure.i18n import (
            I18nMenusLoader,
            I18nMessageLoader,
            I18nTablesLoader,
        )

        assert I18nMessageLoader is not None
        assert I18nMenusLoader is not None
        assert I18nTablesLoader is not None


class TestAdapterImports:
    """Test adapter layer imports."""

    def test_cli_controllers_import(self) -> None:
        """Test CLI controller module exports."""
        from archive_manager.adapters.cli import ContactCslController

        assert ContactCslController is not None

    def test_cli_ui_import(self) -> None:
        """Test CLI UI module exports."""
        from archive_manager.adapters.cli.ui import ContactCslUI, CslUI

        assert CslUI is not None
        assert ContactCslUI is not None

    def test_cli_states_import(self) -> None:
        """Test CLI states module exports."""
        from archive_manager.adapters.cli.states import (
            AppContext,
            BaseState,
            MainContactMenuState,
        )

        assert AppContext is not None
        assert MainContactMenuState is not None
        assert BaseState is not None


class TestThirdPartyDependencies:
    """Test third-party dependencies are correctly installed and importable."""

    def test_rich_import(self) -> None:
        """Test Rich library imports."""
        from rich import box
        from rich.console import Console
        from rich.padding import Padding
        from rich.panel import Panel
        from rich.prompt import Prompt
        from rich.table import Table
        from rich.text import Text
        from rich.theme import Theme

        assert box is not None
        assert Console is not None
        assert Padding is not None
        assert Panel is not None
        assert Prompt is not None
        assert Table is not None
        assert Text is not None
        assert Theme is not None

    def test_inquirerpy_import(self) -> None:
        """Test InquirerPy library imports."""
        from InquirerPy.prompts.input import InputPrompt
        from InquirerPy.prompts.list import ListPrompt
        from InquirerPy.separator import Separator
        from InquirerPy.utils import get_style

        assert InputPrompt is not None
        assert ListPrompt is not None
        assert Separator is not None
        assert get_style is not None

    def test_inquirerpy_style_type(self) -> None:
        """Test InquirerPyStyle type can be used."""
        from InquirerPy.utils import InquirerPyStyle

        # InquirerPyStyle is a TypeAlias, verify it exists
        assert InquirerPyStyle is not None

    def test_sqlalchemy_import(self) -> None:
        """Test SQLAlchemy library imports."""
        from sqlalchemy import String, create_engine, select
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
        from sqlalchemy.pool import QueuePool

        assert String is not None
        assert create_engine is not None
        assert select is not None
        assert DeclarativeBase is not None
        assert Mapped is not None
        assert mapped_column is not None
        assert sessionmaker is not None
        assert QueuePool is not None

    def test_decorator_import(self) -> None:
        """Test decorator library import."""
        from decorator import decorator

        assert decorator is not None
