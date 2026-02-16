#!/usr/bin/env python3
"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from archive_manager.adapters.api.deps import ApiContainer
from archive_manager.adapters.api.handlers import register_handlers
from archive_manager.adapters.api.routers import contacts_router
from archive_manager.adapters.api.schemas import HealthResponse
from archive_manager.infrastructure.config import Settings
from archive_manager.infrastructure.i18n import I18nMenus, I18nMessages, I18nTables


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure FastAPI app instance.

    Args:
        settings: Optional settings override (useful for tests).

    Returns:
        Configured FastAPI app.
    """
    app_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        # Configure i18n subsystem
        I18nMessages.configure(app_settings.i18n)
        I18nMenus.configure(app_settings.i18n)
        I18nTables.configure(app_settings.i18n)

        container = ApiContainer.build(app_settings)
        app_instance.state.container = container
        try:
            yield
        finally:
            container.close()

    app = FastAPI(
        title="Archive Manager API",
        version=app_settings.version,
        debug=app_settings.debug,
        lifespan=lifespan,
    )

    app.state.settings = app_settings

    # Register customized exception handlers
    register_handlers(app)

    @app.get("/health", tags=["health"], response_model=HealthResponse)
    def health() -> HealthResponse:
        """Read API health status.

        Returns:
            Basic process health payload.
        """
        return HealthResponse(
            status="ok",
            version=app_settings.version,
            database=app_settings.database.url.split("/")[-1],
        )

    app.include_router(contacts_router, prefix="/api/v1")
    return app


def run(
    *,
    host: str | None = None,
    port: int | None = None,
    reload: bool = False,
) -> None:
    """Run API server using configured settings.

    CLI flags override values from config/env.

    Args:
        host: Override bind host.
        port: Override bind port.
        reload: Enable auto-reload for development.
    """
    settings = Settings()
    uvicorn.run(
        "archive_manager.adapters.api.main:create_app",
        factory=True,
        host=host or settings.api.host,
        port=port or settings.api.port,
        reload=reload or settings.api.reload,
    )
