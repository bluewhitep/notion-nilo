# File: src/nilo/mcp_server/tools/raw_api.py
# Format: UTF-8
# =============================
# File Description:
# MCP tool for registered raw Notion SDK/API operations.
# TAG: mcp, tools, raw-api
# =============================

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from nilo.core.errors import CoreError
from nilo.core.services.raw_api import registered_operations

from .shared import core_error_payload, get_raw_api_service as _get_raw_api_service

DESTRUCTIVE_RAW_OPERATIONS = {"blocks.delete"}


# --------------------------------
# Function Description:
# Detects Raw API calls that delete, archive, or trash Notion content.
# Inputs/Outputs:
# Input operation name and raw arguments; returns whether explicit confirmation is required.
# Usage:
# raw_api_requires_confirmation("blocks.delete", {})
# --------------------------------
def raw_api_requires_confirmation(operation: str, arguments: dict[str, Any]) -> bool:
    if operation in DESTRUCTIVE_RAW_OPERATIONS:
        return True
    return any(arguments.get(key) is True for key in ("archived", "in_trash"))


def get_raw_api_service():
    return _get_raw_api_service()


def register(server: FastMCP) -> None:
    @server.tool(
        name="raw_api_invoke",
        description="Invoke a registered Notion SDK/API operation. Delete/archive/trash calls require confirm=true.",
        annotations=ToolAnnotations(destructiveHint=True),
    )
    def raw_api_invoke(
        operation: str,
        arguments: dict[str, Any] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        call_arguments = arguments or {}
        if raw_api_requires_confirmation(operation, call_arguments) and not confirm:
            return {
                "ok": False,
                "error": {
                    "code": "confirmation_required",
                    "message": "confirm=true is required for destructive Raw API operations",
                },
            }
        try:
            return get_raw_api_service().invoke(operation, call_arguments)
        except CoreError as exc:
            return core_error_payload(exc)

    @server.tool(
        name="raw_api_registered_operations",
        description="List registered raw Notion SDK/API operations.",
    )
    def raw_api_registered_operations() -> dict[str, Any]:
        return {"operations": list(registered_operations())}
