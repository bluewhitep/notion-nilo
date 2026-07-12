# File: src/nilo/dependencies.py
# Format: UTF-8
# =============================
# File Description:
# FastAPI-only dependency adapters for Core configuration, clients, and services.
# TAG: rest, fastapi, dependencies, core
# =============================

from __future__ import annotations

from typing import Any, NoReturn

from fastapi import Depends, HTTPException

from nilo.core.config import CoreConfig, load_core_config
from nilo.core.errors import ConfigNotFoundError, ConfigValidationError, CoreError
from nilo.core.services.blocks import BlocksService
from nilo.core.services.database_compatibility import DatabaseCompatibilityService
from nilo.core.services.pages import PagesService
from nilo.core.services.provider import (
    get_blocks_service as create_blocks_service,
    get_core_client as create_core_client,
    get_database_compatibility_service as create_database_compatibility_service,
    get_pages_service as create_pages_service,
)


# --------------------------------
# Function Description:
# Loads validated Core configuration for the legacy FastAPI adapter.
# Inputs/Outputs:
# No input; returns CoreConfig or raises an HTTP 500 adapter error.
# Usage:
# FastAPI Depends(get_config)
# --------------------------------
def get_config() -> CoreConfig:
    try:
        config = load_core_config()
    except ConfigNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Global configuration file does not exist. Run: nilo config --global user.token <token>",
        ) from exc
    except ConfigValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if not config.notion_token:
        raise HTTPException(
            status_code=500,
            detail="Notion token is not set. Run: nilo config --global user.token <token>",
        )
    return config


# --------------------------------
# Function Description:
# Creates the Notion client through the canonical Core provider.
# Inputs/Outputs:
# Input injected CoreConfig; returns SDK-compatible client or raises HTTP 500.
# Usage:
# FastAPI Depends(get_notion_client)
# --------------------------------
def get_notion_client(config: CoreConfig = Depends(get_config)) -> Any:
    try:
        return create_core_client(config)
    except CoreError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# --------------------------------
# Function Description:
# Creates the Core pages service from the preserved client dependency injection point.
# Inputs/Outputs:
# Input injected client; returns PagesService.
# Usage:
# FastAPI Depends(get_pages_service)
# --------------------------------
def get_pages_service(client: Any = Depends(get_notion_client)) -> PagesService:
    return create_pages_service(client)


# --------------------------------
# Function Description:
# Creates the Core blocks service from the preserved client dependency injection point.
# Inputs/Outputs:
# Input injected client; returns BlocksService.
# Usage:
# FastAPI Depends(get_blocks_service)
# --------------------------------
def get_blocks_service(client: Any = Depends(get_notion_client)) -> BlocksService:
    return create_blocks_service(client)


# --------------------------------
# Function Description:
# Creates the Core database compatibility service for legacy REST routes.
# Inputs/Outputs:
# Input injected client; returns DatabaseCompatibilityService.
# Usage:
# FastAPI Depends(get_database_compatibility_service)
# --------------------------------
def get_database_compatibility_service(
    client: Any = Depends(get_notion_client),
) -> DatabaseCompatibilityService:
    return create_database_compatibility_service(client)


# --------------------------------
# Function Description:
# Converts a Core operation error into the legacy REST HTTP error contract.
# Inputs/Outputs:
# Input CoreError; always raises HTTPException using an SDK status when available.
# Usage:
# raise_core_http_error(error)
# --------------------------------
def raise_core_http_error(error: CoreError) -> NoReturn:
    cause_status = getattr(error.__cause__, "status", None)
    status_code = cause_status if isinstance(cause_status, int) else 502
    raise HTTPException(status_code=status_code, detail=str(error)) from error


__all__ = [
    "get_blocks_service",
    "get_config",
    "get_database_compatibility_service",
    "get_notion_client",
    "get_pages_service",
    "raise_core_http_error",
]
