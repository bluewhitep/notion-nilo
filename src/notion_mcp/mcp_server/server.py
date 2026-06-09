# File: src/notion_mcp/mcp_server/server.py
# Format: UTF-8
# =============================
# File Description:
# FastMCP server factory and transport entrypoints for Notion MCP tools.
# TAG: mcp, server, fastmcp
# =============================

from __future__ import annotations

import json
from typing import Any, Literal, cast

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .tools import (
    auth,
    blocks,
    comments,
    config,
    custom_emojis,
    data_sources,
    databases,
    file_uploads,
    pages,
    raw_api,
    search,
    users,
    views,
)

DESTRUCTIVE_TOOLS = {"page_trash", "block_trash"}


class NotionFastMCP(FastMCP):
    # --------------------------------
    # Function Description:
    # Registers tools as unstructured text-output tools unless explicitly overridden.
    # Inputs/Outputs:
    # Input FastMCP tool metadata; returns a decorator that registers the tool.
    # Usage:
    # @server.tool(name="config_status")
    # --------------------------------
    def tool(
        self,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        annotations: Any | None = None,
        icons: list[Any] | None = None,
        meta: dict[str, Any] | None = None,
        structured_output: bool | None = None,
    ):
        if structured_output is None:
            structured_output = False
        return super().tool(
            name=name,
            title=title,
            description=description,
            annotations=annotations,
            icons=icons,
            meta=meta,
            structured_output=structured_output,
        )

    # --------------------------------
    # Function Description:
    # Calls tools with a pre-validation confirmation check for destructive tools.
    # Inputs/Outputs:
    # Input tool name and arguments; returns MCP content blocks.
    # Usage:
    # await server.call_tool("page_trash", {"page_id": "id"})
    # --------------------------------
    async def call_tool(self, name: str, arguments: dict[str, Any]):
        if name in DESTRUCTIVE_TOOLS and not arguments.get("confirm"):
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "ok": False,
                            "error": {
                                "code": "confirmation_required",
                                "message": "confirm=true is required for this destructive tool",
                            },
                        },
                        ensure_ascii=False,
                    ),
                )
            ]
        result = await super().call_tool(name, arguments)
        if isinstance(result, tuple) and result and isinstance(result[0], list):
            return result[0]
        return result

    # --------------------------------
    # Function Description:
    # Lists tools and marks destructive tool schemas as requiring confirm.
    # Inputs/Outputs:
    # No input; returns MCP tool metadata list.
    # Usage:
    # await server.list_tools()
    # --------------------------------
    async def list_tools(self):
        tools = await super().list_tools()
        for tool in tools:
            if tool.name in DESTRUCTIVE_TOOLS:
                required = list(tool.inputSchema.get("required", []))
                if "confirm" not in required:
                    required.append("confirm")
                tool.inputSchema["required"] = required
        return tools


# --------------------------------
# Function Description:
# Returns supported MCP transports for the local server.
# Inputs/Outputs:
# No input; returns tuple of transport names.
# Usage:
# supported_transports()
# --------------------------------
def supported_transports() -> tuple[str, ...]:
    return ("stdio", "streamable-http")


# --------------------------------
# Function Description:
# Creates a FastMCP server and registers all Notion tools.
# Inputs/Outputs:
# No input; returns configured FastMCP server.
# Usage:
# server = create_mcp_server()
# --------------------------------
def create_mcp_server(*, host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    server = NotionFastMCP(
        "notion-mcp",
        instructions="Local Notion MCP server backed by Core services.",
        host=host,
        port=port,
    )
    for module in [
        config,
        auth,
        pages,
        blocks,
        databases,
        data_sources,
        users,
        comments,
        views,
        file_uploads,
        search,
        custom_emojis,
        raw_api,
    ]:
        module.register(server)
    return server


# --------------------------------
# Function Description:
# Starts the MCP server with the requested transport.
# Inputs/Outputs:
# Input transport name; output is a running MCP server process.
# Usage:
# serve(transport="stdio")
# --------------------------------
def serve(transport: str = "stdio", *, host: str = "127.0.0.1", port: int = 8000) -> None:
    if transport not in supported_transports():
        raise ValueError(f"Unsupported MCP transport: {transport}")
    typed_transport = cast(Literal["stdio", "sse", "streamable-http"], transport)
    create_mcp_server(host=host, port=port).run(transport=typed_transport)
