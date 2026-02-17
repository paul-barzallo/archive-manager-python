#!/usr/bin/env python3
"""Console UI helpers: enhanced output for the CLI using Rich library.

This module provides utilities for beautiful, styled console output that works
consistently across Windows, Linux, and macOS. It uses the Rich library for
advanced formatting, tables, panels, and interactive prompts.

All text displayed is provided through I18nMessages class for i18n support.
The language is passed as parameter from AppContext to each method.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any, ClassVar, cast

from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import get_style
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.theme import Theme

from archive_manager.infrastructure.i18n import I18nMenu, I18nMessages, I18nTable

# Custom theme for consistent styling
_THEME = Theme(
    {
        "info": "cyan1",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "prompt": "bold cyan1",
        "title": "bold cyan1",
        "menu": "cyan1",
        "menu_title": "bold cyan1",
        "prompt.default": "cyan1",
    }
)

# InquirerPy style for interactive prompts
_INQUIRER_STYLE = get_style(
    {
        "question": "bold cyan",
        "answer": "cyan",
        "pointer": "cyan",
        "marker": "bold green",
        "separator": "bold cyan",
        "instruction": "dim",
    },
    style_override=False,
)

# Banner and UI are rendered with a themed console per instance
_TITLE = r"""
     █████╗  ██████╗   ██████╗ ██╗  ██╗ ██╗ ██╗   ██╗ ███████╗
    ██╔══██╗ ██╔══██╗ ██╔════╝ ██║  ██║ ██║ ██║   ██║ ██╔════╝
    ███████║ ██████╔╝ ██║      ███████║ ██║ ██║   ██║ █████╗
    ██╔══██║ ██╔══██╗ ██║      ██╔══██║ ██║ ╚██╗ ██╔╝ ██╔══╝
    ██║  ██║ ██║  ██║ ╚██████╗ ██║  ██║ ██║  ╚████╔╝  ███████╗
    ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚═╝   ╚═══╝   ╚══════╝
███╗   ███╗  █████╗  ███╗   ██╗  █████╗   ██████╗  ███████╗ ██████╗
████╗ ████║ ██╔══██╗ ████╗  ██║ ██╔══██╗ ██╔════╝  ██╔════╝ ██╔══██╗
██╔████╔██║ ███████║ ██╔██╗ ██║ ███████║ ██║  ███╗ █████╗   ██████╔╝
██║╚██╔╝██║ ██╔══██║ ██║╚██╗██║ ██╔══██║ ██║   ██║ ██╔══╝   ██╔══██╗
██║ ╚═╝ ██║ ██║  ██║ ██║ ╚████║ ██║  ██║ ╚██████╔╝ ███████╗ ██║  ██║
╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═══╝ ╚═╝  ╚═╝  ╚═════╝  ╚══════╝ ╚═╝  ╚═╝"""


class CslUI:
    """Base UI class encapsulating Rich rendering and i18n support.

    Provides methods for displaying styled output including menus, tables, panels
    with colors, and interactive prompts. All text is localized through the
    I18nMessages class for i18n support.

    Subclasses must define _I18N to specify which message class to use.
    Language is passed as parameter to methods that need localized text.
    """

    _I18N: ClassVar[type[I18nMessages]] = I18nMessages

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the UI with Rich console.

        Args:
            console: Optional Rich Console instance (creates a new one if `None`).
        """
        self._console = console or Console(theme=_THEME)

    def clear_screen(self) -> None:
        """Clear the console screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def show_title(self) -> None:
        """Display the application title with banner."""
        self.clear_screen()
        title_text = Text(_TITLE, style="title")
        panel = Panel(title_text, border_style="none", box=box.SIMPLE, padding=(0, 0))
        self._console.print(panel)

    def print_errors(
        self, language: str, errors: Sequence[dict[str, dict[str, Any]]]
    ) -> None:
        """Display multiple error messages in a panel.

        Args:
            language: Language code for i18n.
            errors: Sequence of error dicts mapping codes to kwargs.
        """
        error_messages: list[str] = []
        for err in errors:
            for code, kwargs in err.items():
                error_messages.append(
                    self._I18N.error(language, code).formatted_message(**kwargs)
                )
        self.print_error_base(language, "\n".join(error_messages))

    def print_error(
        self, language: str, code: str, details: str | None = None, **kwargs: Any
    ) -> None:
        """Display an error message by code.

        Args:
            language: Language code for i18n.
            code: Error message code for i18n lookup.
            details: Optional additional details.
            **kwargs: Format parameters for the message.
        """
        message = self._I18N.error(language, code).formatted_message(**kwargs)
        self.print_error_base(language, message, details)

    def print_error_base(
        self, language: str, message: str, details: str | None = None
    ) -> None:
        """Display an error message in a red panel.

        Args:
            language: Language code for i18n.
            message: Error message to display.
            details: Optional detailed error information.
        """
        title = self._I18N.field(language, "TITLE_ERROR")
        content = f"[bold red]{message}[/bold red]"
        if details:
            content += f"\n\n[dim]{details}[/dim]"
        panel = Panel(
            content,
            title=f"[bold red]{title}[/bold red]",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        self._console.print()
        self._console.print(Padding(panel, (0, 2)))

    def print_warning(self, language: str, code: str, **kwargs: Any) -> None:
        """Display a warning message in a yellow panel.

        Args:
            language: Language code for i18n.
            code: Warning message code for i18n lookup.
            **kwargs: Format parameters for the message.
        """
        title = self._I18N.field(language, "TITLE_WARNING")
        message = self._I18N.warning(language, code).formatted_message(**kwargs)
        panel = Panel(
            f"[bold yellow]{message}[/bold yellow]",
            title=f"[bold yellow]{title}[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        self._console.print()
        self._console.print(Padding(panel, (0, 2)))

    def print_success(self, language: str, code: str) -> None:
        """Display a success message in a green panel.

        Args:
            language: Language code for i18n.
            code: Success message code to display.
        """
        title = self._I18N.field(language, "TITLE_SUCCESS")
        message = self._I18N.success(language, code).message
        panel = Panel(
            f"[bold green]{message}[/bold green]",
            title=f"[bold green]{title}[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        self._console.print()
        self._console.print(Padding(panel, (0, 2)))

    def print_info(
        self, language: str, code: str, title: str | None = None, **kwargs: Any
    ) -> None:
        """Display an information message in a cyan panel.

        Args:
            language: Language code for i18n.
            code: Information message code for i18n lookup.
            title: Optional custom title (defaults to localized 'TITLE_INFORMATION').
            **kwargs: Format parameters for the message.
        """
        if title is None:
            title = self._I18N.field(language, "TITLE_INFORMATION")
        message = self._I18N.info(language, code, **kwargs)
        panel = Panel(
            f"[cyan1]{message}[/cyan1]",
            title=f"[bold cyan1]{title}[/bold cyan1]",
            border_style="cyan1",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        self._console.print(Padding(panel, (0, 2)))

    def get_input(
        self, language: str, prompt_code: str, default: str = "", password: bool = False
    ) -> str:
        """Prompt the user for text input.

        Args:
            language: Language code for i18n.
            prompt_code: I18n code for the prompt message.
            default: Default value if user presses Enter.
            password: If `True`, input is masked (for passwords).

        Returns:
            The user's input (stripped of whitespace).
        """
        prompt = self._I18N.prompt(language, prompt_code)
        self._console.print()
        result = InputPrompt(
            message=f" {prompt}:",
            default=default,
            qmark="",
            amark="",
            instruction="",
            long_instruction="",
            style=_INQUIRER_STYLE,
            is_password=password,
        ).execute()
        return (result or "").strip()

    def confirm(self, language: str, confirm_code: str) -> bool:
        """Prompt the user for a yes/no confirmation.

        Args:
            language: Language code for i18n.
            confirm_code: I18n code for the confirmation message.

        Returns:
            `True` if user confirms, `False` otherwise.
        """
        choices: list[dict[str, Any]] = cast(
            list[dict[str, Any]],
            [
                Separator(self._I18N.confirm(language, confirm_code)),
                Separator(""),
                {"name": f"{self._I18N.confirm(language, 'YES')}", "value": True},
                {"name": f"{self._I18N.confirm(language, 'NO')}", "value": False},
            ],
        )

        return bool(
            ListPrompt(
                message="",
                choices=choices,
                qmark="",
                amark="",
                pointer=">",
                instruction="",
                long_instruction="",
                style=_INQUIRER_STYLE,
                show_cursor=False,
                cycle=True,
            ).execute()
        )

    def cancel(self, language: str) -> None:
        """Display a cancellation message."""
        self.print_info(language, "INFO_OPERATION_CANCELLED")

    def pause(self, language: str) -> None:
        """Pause execution and wait for user to press Enter."""
        message = self._I18N.prompt(language, "PROMPT_PRESS_ENTER")
        self._console.print()
        Prompt.ask(f" [dim]{message} [/dim]", console=self._console, show_default=False)

    def _show_menu(self, menu_config: I18nMenu, clear_screen: bool = True) -> str:
        """Display a menu and return the selected option ID.

        Args:
            menu_config: ``I18nMenu`` instance to display.
            clear_screen: If ``True``, render the banner and clear previous output.

        Returns:
            The ID of the selected menu option.
        """
        if clear_screen:
            self.show_title()
        return menu_config.prompt_choice(_INQUIRER_STYLE)

    def _show_table(
        self, table_config: I18nTable, data: Sequence[Any], **kwargs: Any
    ) -> None:
        """Display a table with the provided data.

        Args:
            table_config: ``I18nTable`` instance defining table structure.
            data: Sequence of objects to display in the table.
            **kwargs: Footer formatting values used by ``I18nTable``.
        """
        table = table_config.build_table([vars(element) for element in data], **kwargs)
        self._console.print()
        self._console.print(Padding(table, (0, 2)))
        self._console.print()

    def _show_details(self, title: str, labels: Sequence[dict[str, str]]) -> None:
        """Display detailed information in a formatted panel.

        Args:
            title: Panel title.
            labels: Sequence of dicts with 'text' and 'value' keys.
        """
        details = ""
        for label in labels:
            details += f"[bold cyan1]{label['text']}:[/bold cyan1] {label['value']}\n"

        panel = Panel(
            details,
            title=f"[bold cyan1]{title}[/bold cyan1]",
            border_style="cyan1",
            box=box.ROUNDED,
            padding=(1, 1, 0, 1),
        )
        self._console.print()
        self._console.print(Padding(panel, (0, 2)))
