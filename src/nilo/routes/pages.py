# File: src/nilo/routes/pages.py
# Format: UTF-8
# =============================
# File Description:
# Legacy page REST routes delegating all Notion operations to Core services.
# TAG: rest, routes, pages, core
# =============================

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends

from nilo.core.errors import CoreError
from nilo.core.services.pages import PagesService

from ..dependencies import get_pages_service, raise_core_http_error


router = APIRouter(prefix="/pages", tags=["pages"])


@router.get("/{page_id}")
# --------------------------------
# Function Description:
# Retrieves a page through the Core pages service.
# Inputs/Outputs:
# Input page id and injected service; returns Notion page response.
# Usage:
# GET /pages/{page_id}
# --------------------------------
async def get_page(
    page_id: str,
    service: PagesService = Depends(get_pages_service),
) -> dict[str, Any]:
    try:
        return service.retrieve(page_id)
    except CoreError as exc:
        raise_core_http_error(exc)


@router.post("/")
# --------------------------------
# Function Description:
# Creates a page through the Core pages service.
# Inputs/Outputs:
# Input JSON body and injected service; returns Notion create response.
# Usage:
# POST /pages
# --------------------------------
async def create_page(
    body: dict[str, Any] = Body(...),
    service: PagesService = Depends(get_pages_service),
) -> dict[str, Any]:
    try:
        return service.create(body)
    except CoreError as exc:
        raise_core_http_error(exc)


@router.patch("/{page_id}")
# --------------------------------
# Function Description:
# Updates a page through the Core pages service.
# Inputs/Outputs:
# Input page id, JSON body, and injected service; returns Notion update response.
# Usage:
# PATCH /pages/{page_id}
# --------------------------------
async def update_page(
    page_id: str,
    body: dict[str, Any] = Body(...),
    service: PagesService = Depends(get_pages_service),
) -> dict[str, Any]:
    try:
        return service.update(page_id, body)
    except CoreError as exc:
        raise_core_http_error(exc)
