#!/usr/bin/env python3
"""Application settings using Pydantic.

Settings are created once in the application entry point and injected
into components that need them. There is no global singleton.
"""

from __future__ import annotations

import locale
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from archive_manager.infrastructure.config.logging import configure_logging

logger = logging.getLogger(__name__)

# Package root (where archive_manager is installed)
_PACKAGE_DIR = Path(__file__).resolve().parent.parent.parent

# Project root (for config.yaml — only relevant when running from repo)
_PROJECT_DIR = _PACKAGE_DIR.parent.parent

# Package resources (shipped with the package)
_I18N_PATH = _PACKAGE_DIR / "resources" / "i18n"

# Default data directory (relative to project root)
_DATA_DIR = _PROJECT_DIR / "data"

# Config file (project root)
_CONFIG_FILE = _PROJECT_DIR / "config.yaml"

# Environment file (project root)
_ENV_FILE = _PROJECT_DIR / ".env"

# Default language
DEFAULT_LANGUAGE = "en"


class DatabaseSettings(BaseSettings):
    """Database settings."""

    model_config = SettingsConfigDict(extra="ignore")

    url: str = Field(default=f"sqlite:///{_DATA_DIR / 'db' / 'archive-manager.sqlite'}")
    pool_size: int = Field(default=5, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=100)
    pool_recycle: int = Field(default=3600, ge=0)
    echo: bool = Field(default=False)


class LoggingSettings(BaseSettings):
    """Logging settings."""

    model_config = SettingsConfigDict(extra="ignore")

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    dir: Path = Field(default=_DATA_DIR / "logs")
    format: str = Field(default="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")

    @field_validator("dir", mode="before")
    @classmethod
    def ensure_path(cls, v: str | Path) -> Path:
        """Ensure value is a Path object.

        Args:
            v: String or Path value to validate.

        Returns:
            Path object.
        """
        return Path(v) if isinstance(v, str) else v


class I18nSettings(BaseSettings):
    """Internationalization settings."""

    model_config = SettingsConfigDict(extra="ignore")

    language: str = Field(default="")
    i18n_path: Path = Field(default=_I18N_PATH)
    available_languages: Sequence[str] = []

    def model_post_init(self, __context: Any) -> None:
        """Validate languages on initialization."""
        # Use object.__setattr__ because Pydantic models are frozen by default
        object.__setattr__(self, "available_languages", self._get_available_languages())
        self._validate_default_language()
        if (
            self.language
            and self.language != DEFAULT_LANGUAGE
            and not self.valid_language(self.language)
        ):
            logger.warning("Configured language '%s' is invalid.", self.language)
            object.__setattr__(self, "language", "")

    @field_validator("i18n_path", mode="before")
    @classmethod
    def _ensure_path(cls, v: str | Path) -> Path:
        """Ensure value is a Path object.

        Args:
            v: String or Path value to validate.

        Returns:
            Path object.
        """
        return Path(v) if isinstance(v, str) else v

    def get_file_path(
        self, language: str, service: str | None = None, *subdirs: str, filename: str
    ) -> Path:
        """Get path to a language-specific i18n file.

        Args:
            language: Language code (e.g., 'en', 'es').
            filename: JSON filename.
            subdirs: Subdirectories (e.g., 'internal', 'output').
            service: Optional service name (e.g., 'contacts').

        Returns:
            Full path to the i18n file.
        """
        path = self.i18n_path / language
        if service:
            path = path / service
        for subdir in subdirs:
            path = path / subdir
        return path / filename

    def _get_available_languages(self) -> Sequence[str]:
        """Get Sequence of available languages with complete file sets.

        Scans the i18n directory for language folders that contain
        all required message files.

        Returns:
            Sorted Sequence of valid language codes.
        """
        required_files = (
            "visual/confirm.json",
            "visual/info.json",
            "visual/fields.json",
            "visual/prompts.json",
            "output/error.json",
            "output/success.json",
            "output/warning.json",
        )
        languages: list[str] = []
        if not self.i18n_path.exists():
            return languages

        for lang_dir in self.i18n_path.iterdir():
            if lang_dir.is_dir():
                global_valid = all(
                    (lang_dir / req_file).exists() for req_file in required_files
                )
                if global_valid:
                    languages.append(lang_dir.name)

        return sorted(languages)

    def _validate_default_language(self) -> None:
        """Validate that the default language exists and is complete.

        Raises:
            SystemExit: If default language is missing or incomplete.
        """
        if not self.valid_language(DEFAULT_LANGUAGE):
            sys.exit(
                f"FATAL: Default language '{DEFAULT_LANGUAGE}' is missing or "
                f"incomplete. Ensure all required files exist in "
                f"{self.i18n_path / DEFAULT_LANGUAGE}/"
            )

    def valid_language(self, language: str) -> bool:
        """Validate that the language exists and is complete.

        Args:
            language: Language code to check.

        Returns:
            ``True`` if language is available, ``False`` otherwise.
        """
        return language in self.available_languages


class Settings(BaseSettings):
    """Main application settings (immutable after initialization).

    Configuration precedence (highest to lowest):
    1. ``--debug`` CLI flag
    2. Init kwargs (for testing/programmatic override)
    3. Environment variables (``APP_`` prefix, ``__`` nested delimiter)
    4. ``.env`` file (secrets and per-machine overrides)
    5. ``config.{environment}.yaml`` file (environment-specific)
    6. ``config.yaml`` file (base configuration)
    7. Field defaults

    Environment-specific configuration:
        - Set 'environment' in config.yaml (development, testing, production)
        - Create config.{environment}.yaml (e.g., config.production.yaml)
        - Environment config deeply merges with base config

    Example:
        config.yaml (base)::

            environment: production
            database:
                echo: false
                pool_size: 5

        config.production.yaml::

            database:
                pool_size: 20

        Result::

            database:
                echo: false
                pool_size: 20
    """

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="APP_",
        env_nested_delimiter="__",
    )

    app_name: str = Field(default="archive-manager")
    version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    environment: Literal["development", "testing", "production"] = Field(
        default="development"
    )

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    i18n: I18nSettings = Field(default_factory=I18nSettings)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings from config files, env vars, and kwargs.

        Configuration precedence (highest to lowest):
        1. kwargs (programmatic overrides)
        2. Environment variables / .env file (APP_ prefix)
        3. config.{environment}.yaml (environment-specific)
        4. config.yaml (base configuration)
        5. Field defaults

        Args:
            **kwargs: Override values (take precedence over config files).
        """
        cli_debug = self._detect_debug_flag()
        if cli_debug:
            kwargs["debug"] = True

        # Load base config.yaml
        yaml_config = self._load_yaml(_CONFIG_FILE)

        # Get environment from kwargs or base config
        environment = kwargs.get("environment") or yaml_config.get(
            "environment", "development"
        )

        # Load environment-specific config
        env_config_file = _PROJECT_DIR / f"config.{environment}.yaml"
        env_config = self._load_yaml(env_config_file)

        # Merge: base config < env config < kwargs
        merged = self._deep_merge(yaml_config, env_config)
        merged = self._deep_merge(merged, kwargs)

        super().__init__(**merged)

    @staticmethod
    def _load_yaml(config_path: Path) -> dict[str, Any]:
        """Load configuration from a YAML file.

        Args:
            config_path: Path to the YAML configuration file.

        Returns:
            Configuration dictionary, empty if file doesn't exist.
        """
        if config_path.exists():
            with Path.open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries.

        Values from override take precedence. Nested dicts are merged recursively.

        Args:
            base: Base dictionary.
            override: Dictionary with override values.

        Returns:
            Merged dictionary.
        """
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = Settings._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to configure logging."""
        configure_logging(
            level=self.logging.level,
            log_dir=self.logging.dir,
            log_format=self.logging.format,
            date_format=self.logging.date_format,
            debug=self.debug,
        )

    def get_system_language(self) -> str:
        """Detect language from system locale.

        Returns:
            Two-letter language code if valid, empty string otherwise.
        """
        try:
            lang, _ = locale.getlocale()
            if lang:
                code = lang[:2].lower()
                if self.i18n.valid_language(code):
                    return code
        except Exception:
            logger.warning("Failed to detect system locale.", exc_info=True)

        return ""

    @staticmethod
    def _detect_debug_flag() -> bool:
        """Detect and consume ``--debug`` flag from command line.

        Returns:
            ``True`` if ``--debug`` was present in sys.argv.
        """
        if "--debug" in sys.argv:
            sys.argv.remove("--debug")
            return True
        return False

    @classmethod
    def for_testing(cls) -> Settings:
        """Create settings instance configured for testing.

        Returns:
            Settings with in-memory database and debug logging.
        """
        return cls(
            environment="testing",
            debug=True,
            database=DatabaseSettings(url="sqlite:///:memory:"),
            logging=LoggingSettings(level="DEBUG"),
        )
