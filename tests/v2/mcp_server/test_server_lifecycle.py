import pytest
from mcp.server.fastmcp import FastMCP

from nilo.core.config_constants import SUPPORTED_TRANSPORTS
from nilo.mcp_server.server import create_mcp_server, supported_transports


@pytest.mark.asyncio
async def test_mcp_server_initializes_and_lists_tools() -> None:
    server = create_mcp_server()

    tools = await server.list_tools()

    assert isinstance(server, FastMCP)
    assert server.name == "nilo"
    assert tools


def test_supported_transports_include_stdio_and_streamable_http() -> None:
    transports = supported_transports()

    assert transports == SUPPORTED_TRANSPORTS == ("stdio", "streamable-http")
