# File: src/nilo/mcp_server/tools/shared.py
# Format: UTF-8
# =============================
# File Description:
# MCP-specific error formatting plus Core-owned service constructor imports.
# TAG: mcp, tools, core-services, errors
# =============================

from __future__ import annotations

from typing import Any

from nilo.core.errors import CoreError
from nilo.core.services.provider import (
    get_blocks_service,
    get_comments_service,
    get_core_client,
    get_custom_emojis_service,
    get_data_sources_service,
    get_databases_service,
    get_file_uploads_service,
    get_pages_service,
    get_raw_api_service,
    get_search_service,
    get_users_service,
    get_views_service,
)


# --------------------------------
# Function Description:
# Converts a Core error to the MCP tool error payload contract.
# Inputs/Outputs:
# Input CoreError; returns a JSON-compatible dictionary.
# Usage:
# core_error_payload(error)
# --------------------------------
def core_error_payload(error: CoreError) -> dict[str, Any]:
    return {"ok": False, "error": error.to_dict()}


__all__ = [
    "core_error_payload",
    "get_blocks_service",
    "get_comments_service",
    "get_core_client",
    "get_custom_emojis_service",
    "get_data_sources_service",
    "get_databases_service",
    "get_file_uploads_service",
    "get_pages_service",
    "get_raw_api_service",
    "get_search_service",
    "get_users_service",
    "get_views_service",
]
