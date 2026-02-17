#!/usr/bin/env python3
"""Unit tests for the application entry point / dispatcher."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from archive_manager import main


def test_no_args_shows_help() -> None:
    """Invoking without arguments should show help and exit."""
    with patch("sys.argv", ["archive-manager"]), pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_cli_subcommand_invokes_cli() -> None:
    """Invoking `cli` subcommand should call CLI main."""
    with (
        patch("sys.argv", ["archive-manager", "cli"]),
        patch("archive_manager.adapters.cli.main") as mock_cli,
    ):
        main()
        mock_cli.assert_called_once()


def test_api_subcommand_invokes_api() -> None:
    """Invoking `api` subcommand should call API run."""
    with (
        patch("sys.argv", ["archive-manager", "api"]),
        patch("archive_manager.adapters.api.run") as mock_api,
    ):
        main()
        mock_api.assert_called_once_with(host=None, port=None, reload=False)


def test_api_subcommand_passes_args() -> None:
    """API subcommand should pass parsed arguments to run."""
    with (
        patch(
            "sys.argv",
            [
                "archive-manager",
                "api",
                "--host",
                "0.0.0.0",
                "--port",
                "9000",
                "--reload",
            ],
        ),
        patch("archive_manager.adapters.api.run") as mock_api,
    ):
        main()
        mock_api.assert_called_once_with(host="0.0.0.0", port=9000, reload=True)
