# File: src/nilo/mcp_server/tools/config.py
# Format: UTF-8
# =============================
# File Description:
# MCP tools for local configuration status and reads.
# TAG: mcp, tools, config
# =============================

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from nilo.core.config import load_core_config, redacted_config
from nilo.core.errors import ConfigNotFoundError, CoreError

from .shared import core_error_payload


# --------------------------------
# Function Description:
# Registers config MCP tools.
# Inputs/Outputs:
# Input FastMCP server; output is server with config tools.
# Usage:
# register(server)
# --------------------------------
def register(server: FastMCP) -> None:
    @server.tool(
        name="config_status",
        description="Return local Notion MCP configuration status with token redacted.",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    def config_status() -> dict[str, Any]:
        try:
            config = load_core_config()
            public = redacted_config(config)
            configured = True
        except ConfigNotFoundError:
            public = {}
            configured = False
        except CoreError as exc:
            return core_error_payload(exc)
        return {
            "configured": configured,
            "config": public,
            "capabilities": {
                "core": True,
                "mcp_server": True,
            },
        }

    @server.tool(
        name="config_get",
        description="Read one local configuration key. Secret values are always redacted.",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    def config_get(key: str) -> dict[str, Any]:
        try:
            config = load_core_config()
        except CoreError as exc:
            return core_error_payload(exc)
        return {"key": key, "value": redacted_config(config).get(key)}
