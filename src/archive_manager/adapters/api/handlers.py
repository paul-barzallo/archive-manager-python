#!/usr/bin/env python3
"""Exception handlers for the API adapter."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from archive_manager.adapters.api.schemas import (
    ErrorDetail,
    ErrorResponse,
)
from archive_manager.core.errors import (
    AppError,
    AppInfrastructureError,
    AppValidationErrors,
    AppWarning,
)
from archive_manager.infrastructure.i18n import ContactI18nMessages


def get_language(request: Request) -> str:
    """Extract language from request headers or use default.

    Args:
        request: FastAPI request object.

    Returns:
        ISO language code (e.g., 'es', 'en').
    """
    accept_lang = request.headers.get("accept-language", "")
    # Simple extraction for first language code: 'es-ES,es;q=0.9,en;q=0.8' -> 'es'
    return accept_lang.split(",")[0].split("-")[0] or "en"


def _resolve_error_message(
    code: str, language: str, is_warning: bool = False
) -> tuple[str, int]:
    """Resolve localized message and default HTTP status from i18n.

    Args:
        code: Error code.
        language: Target language.
        is_warning: Whether to look in warnings or errors.

    Returns:
        Tuple of (message, http_status).
    """
    if is_warning:
        msg = ContactI18nMessages.warning(language, code)
    else:
        msg = ContactI18nMessages.error(language, code)

    return msg.message, msg.http_status


def register_handlers(app: FastAPI) -> None:
    """Register all application exception handlers.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(AppValidationErrors)
    async def validation_errors_handler(
        request: Request,
        exc: AppValidationErrors,
    ) -> JSONResponse:
        lang = get_language(request)
        details: list[ErrorDetail] = []
        for err in exc.errors:
            # For validation errors, we usually have many small errors
            # We look them up as warnings or errors based on code
            _message, _ = _resolve_error_message(err.code, lang, is_warning=True)
            details.append(
                ErrorDetail(
                    code=err.code,
                    origin=err.origin,
                    field=err.field,
                    context=err.context,
                )
            )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                detail="Validation failed" if lang == "en" else "Validación fallida",
                status=status.HTTP_400_BAD_REQUEST,
                errors=details,
            ).model_dump(),
        )

    @app.exception_handler(AppWarning)
    async def app_warning_handler(request: Request, exc: AppWarning) -> JSONResponse:
        lang = get_language(request)
        message, http_status = _resolve_error_message(exc.code, lang, is_warning=True)
        http_status = http_status or status.HTTP_404_NOT_FOUND

        return JSONResponse(
            status_code=http_status,
            content=ErrorResponse(
                detail=message,
                status=http_status,
                errors=[
                    ErrorDetail(
                        code=exc.code,
                        origin=exc.origin,
                        field=exc.field,
                        context=exc.context,
                    )
                ],
            ).model_dump(),
        )

    @app.exception_handler(AppError)
    @app.exception_handler(AppInfrastructureError)
    async def app_error_handler(
        request: Request, exc: AppError | AppInfrastructureError
    ) -> JSONResponse:
        lang = get_language(request)
        is_infra = isinstance(exc, AppInfrastructureError)
        message, http_status = _resolve_error_message(exc.code, lang)

        if not http_status:
            http_status = (
                status.HTTP_500_INTERNAL_SERVER_ERROR
                if is_infra
                else status.HTTP_409_CONFLICT
            )

        return JSONResponse(
            status_code=http_status,
            content=ErrorResponse(
                detail=message,
                status=http_status,
                errors=[
                    ErrorDetail(
                        code=exc.code,
                        origin=exc.origin,
                        field=exc.field,
                        context=exc.context,
                    )
                ],
            ).model_dump(),
        )
