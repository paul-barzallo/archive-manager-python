#!/usr/bin/env python3
"""Archive Manager — Contact Management Application.

Supports multiple delivery mechanisms:
    archive-manager cli   → Interactive console (Rich + InquirerPy)
    archive-manager api   → REST server (FastAPI + Uvicorn)
    archive-manager       → Shows available commands

Architecture: Clean Architecture (core → application → infrastructure → adapters).
"""

import argparse
import sys


def main() -> None:
    """Dispatch to the requested adapter (cli | api)."""
    parser = argparse.ArgumentParser(
        prog="archive-manager",
        description="Archive Manager — Contact Management Application",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── CLI ──────────────────────────────────────────────────────────────
    subparsers.add_parser("cli", help="Launch interactive console")

    # ── API ──────────────────────────────────────────────────────────────
    api_parser = subparsers.add_parser("api", help="Start REST API server")
    api_parser.add_argument("--host", type=str, default=None, help="Bind host")
    api_parser.add_argument("--port", type=int, default=None, help="Bind port")
    api_parser.add_argument(
        "--reload", action="store_true", default=False, help="Enable auto-reload"
    )

    args = parser.parse_args()

    if args.command == "cli":
        from archive_manager.adapters.cli import main as cli_main

        cli_main()

    elif args.command == "api":
        from archive_manager.adapters.api import run as api_run

        api_run(host=args.host, port=args.port, reload=args.reload)

    else:
        parser.print_help()
        sys.exit(0)


__all__ = ["main"]
