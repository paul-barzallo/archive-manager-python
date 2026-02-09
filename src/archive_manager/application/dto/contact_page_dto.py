#!/usr/bin/env python3
"""Data Transfer Object for paginated contact list responses."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from archive_manager.application.dto.contact_dto import ContactDTO


@dataclass(frozen=True)
class ContactPageDTO:
    """Paginated contact list response.

    Includes navigation flags and derived counters for presentation layers.
    """

    contacts: Sequence[ContactDTO]
    total: int
    limit: int
    offset: int

    @property
    def shown(self) -> int:
        """Number of contacts in the current page."""
        return len(self.contacts)

    @property
    def total_pages(self) -> int:
        """Total number of pages for the current ``total`` and ``limit``."""
        if self.total <= 0:
            return 0
        safe_limit = max(1, self.limit)
        return (self.total + safe_limit - 1) // safe_limit

    @property
    def current_page(self) -> int:
        """Current 1-based page index."""
        if self.total_pages == 0:
            return 0
        safe_limit = max(1, self.limit)
        page = (self.offset // safe_limit) + 1
        return min(page, self.total_pages)

    @property
    def start_item(self) -> int:
        """1-based index of the first item shown in this page."""
        if self.shown == 0:
            return 0
        return self.offset + 1

    @property
    def end_item(self) -> int:
        """1-based index of the last item shown in this page."""
        if self.shown == 0:
            return 0
        return self.offset + self.shown

    @property
    def has_next(self) -> bool:
        """Whether there is at least one next page."""
        return self.offset + self.shown < self.total

    @property
    def has_previous(self) -> bool:
        """Whether there is at least one previous page."""
        return self.offset > 0
