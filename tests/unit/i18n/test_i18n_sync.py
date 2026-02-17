#!/usr/bin/env python3
"""Tests for i18n file synchronization between languages."""

from __future__ import annotations

import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
RESOURCES = ROOT / "src" / "archive_manager" / "resources" / "i18n"


def _keys(path: pathlib.Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.keys())


@pytest.mark.parametrize("filename", ["error.json", "warning.json", "success.json"])
def test_contacts_outputs_sync_between_languages(filename):
    """Verify that contacts output messages are synchronized between EN and ES."""
    es = _keys(RESOURCES / "es" / "contact" / "output" / filename)
    en = _keys(RESOURCES / "en" / "contact" / "output" / filename)
    assert es == en, f"Mismatch in contacts/{filename}"


@pytest.mark.parametrize("filename", ["error.json", "warning.json", "success.json"])
def test_global_outputs_sync_between_languages(filename):
    """Verify that global output messages are synchronized between EN and ES."""
    es = _keys(RESOURCES / "es" / "output" / filename)
    en = _keys(RESOURCES / "en" / "output" / filename)
    assert es == en, f"Mismatch in global/{filename}"


def test_menus_json_exists():
    """Verify that menus.json exists for both languages."""
    for lang in ["en", "es"]:
        menus_file = RESOURCES / lang / "contact" / "menus.json"
        assert menus_file.exists(), f"Missing menus.json for {lang}"
        data = json.loads(menus_file.read_text(encoding="utf-8"))
        assert isinstance(data, dict)


def test_contact_menus_sync_between_languages():
    """Verify that contact menu keys are synchronized between EN and ES."""
    es = _keys(RESOURCES / "es" / "contact" / "menus.json")
    en = _keys(RESOURCES / "en" / "contact" / "menus.json")
    assert es == en, "Mismatch in contacts/menus.json"


def test_tables_json_exists():
    """Verify that tables.json exists for both languages."""
    for lang in ["en", "es"]:
        tables_file = RESOURCES / lang / "contact" / "tables.json"
        assert tables_file.exists(), f"Missing tables.json for {lang}"
        data = json.loads(tables_file.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
