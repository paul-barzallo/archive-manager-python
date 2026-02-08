#!/usr/bin/env python3
"""Session configuration for user-specific state.

Provides Session class for managing per-user/session mutable state
like language preferences. Designed to support future multi-user scenarios.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .settings import DEFAULT_LANGUAGE

if TYPE_CHECKING:
    from .settings import I18nSettings

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """User session state.

    Holds mutable per-user configuration like language preference.
    Designed to be instantiated per user/session for future multi-user support.

    Attributes:
        language: Current language code for this session.
    """

    language: str = DEFAULT_LANGUAGE

    def set_language(self, language: str, i18n: I18nSettings) -> bool:
        """Set session language if valid.

        Args:
            language: Language code to set.
            i18n: I18n settings for validating language.

        Returns:
            ``True`` if language was set, ``False`` if invalid.
        """
        if not i18n.valid_language(language):
            logger.warning("Invalid language: %s", language)
            return False
        self.language = language
        return True
