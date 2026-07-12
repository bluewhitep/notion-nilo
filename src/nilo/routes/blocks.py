# File: src/nilo/routes/blocks.py
# Format: UTF-8
# =============================
# File Description:
# Legacy block REST routes delegating all Notion operations to Core services.
# TAG: rest, routes, blocks, core
# =============================

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Body, Depends

from nilo.core.errors import CoreError
from nilo.core.services.blocks import BlocksService

from ..dependencies import get_blocks_service, raise_core_http_error


router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.get("/{block_id}/children")
# --------------------------------
# Function Description:
# Lists child blocks through the Core blocks service.
# Inputs/Outputs:
# Input block id and injected service; returns Notion child listing response.
# Usage:
# GET /blocks/{block_id}/children
# --------------------------------
async def list_block_children(
    block_id: str,
    service: BlocksService = Depends(get_blocks_service),
) -> dict[str, Any]:
    try:
        return service.list_children(block_id)
    except CoreError as exc:
        raise_core_http_error(exc)


@router.post("/{block_id}/append")
# --------------------------------
# Function Description:
# Appends child blocks through the Core blocks service.
# Inputs/Outputs:
# Input block id, JSON body, and injected service; returns append response.
# Usage:
# POST /blocks/{block_id}/append
# --------------------------------
async def append_block_children(
    block_id: str,
    body: dict[str, Any] = Body(...),
    service: BlocksService = Depends(get_blocks_service),
) -> dict[str, Any]:
    children = body.get("children")
    params = {key: value for key, value in body.items() if key != "children"}
    try:
        return service.append_children(
            block_id,
            children=cast(list[dict[str, Any]], children),
            **params,
        )
    except CoreError as exc:
        raise_core_http_error(exc)


@router.patch("/{block_id}")
# --------------------------------
# Function Description:
# Updates a block through the Core blocks service.
# Inputs/Outputs:
# Input block id, JSON body, and injected service; returns Notion update response.
# Usage:
# PATCH /blocks/{block_id}
# --------------------------------
async def update_block(
    block_id: str,
    body: dict[str, Any] = Body(...),
    service: BlocksService = Depends(get_blocks_service),
) -> dict[str, Any]:
    try:
        return service.update(block_id, body)
    except CoreError as exc:
        raise_core_http_error(exc)
