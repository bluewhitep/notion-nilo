# File: src/nilo/routes/databases.py
# Format: UTF-8
# =============================
# File Description:
# Legacy database REST routes delegating compatibility behavior to Core.
# TAG: rest, routes, databases, compatibility, core
# =============================

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException

from nilo.core.errors import CoreError
from nilo.core.services.database_compatibility import DatabaseCompatibilityService

from ..dependencies import get_database_compatibility_service, raise_core_http_error


router = APIRouter(prefix="/databases", tags=["databases"])


@router.get("/")
# --------------------------------
# Function Description:
# Lists database or data-source objects through the Core compatibility service.
# Inputs/Outputs:
# Input object kind and injected service; returns Notion search response.
# Usage:
# GET /databases?kind=data_source
# --------------------------------
async def list_databases(
    kind: str = "data_source",
    service: DatabaseCompatibilityService = Depends(get_database_compatibility_service),
) -> dict[str, Any]:
    if kind not in {"data_source", "database"}:
        raise HTTPException(status_code=400, detail="kind must be data_source or database")
    try:
        return service.list(kind)
    except CoreError as exc:
        raise_core_http_error(exc)


@router.get("/{data_source_id}")
# --------------------------------
# Function Description:
# Retrieves an ambiguous database/data-source id through Core fallback orchestration.
# Inputs/Outputs:
# Input resource id and injected service; returns Notion retrieve response.
# Usage:
# GET /databases/{resource_id}
# --------------------------------
async def retrieve_database(
    data_source_id: str,
    service: DatabaseCompatibilityService = Depends(get_database_compatibility_service),
) -> dict[str, Any]:
    try:
        return service.retrieve(data_source_id)
    except CoreError as exc:
        raise_core_http_error(exc)


@router.post("/{data_source_id}/query")
# --------------------------------
# Function Description:
# Queries an ambiguous database/data-source id through Core fallback orchestration.
# Inputs/Outputs:
# Input resource id, JSON payload, and injected service; returns query response.
# Usage:
# POST /databases/{resource_id}/query
# --------------------------------
async def query_database(
    data_source_id: str,
    payload: dict[str, Any] = Body(default_factory=dict),
    service: DatabaseCompatibilityService = Depends(get_database_compatibility_service),
) -> dict[str, Any]:
    try:
        return service.query(data_source_id, payload)
    except CoreError as exc:
        raise_core_http_error(exc)
