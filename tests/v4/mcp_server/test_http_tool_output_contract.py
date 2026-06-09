import pytest

from notion_mcp.mcp_server.server import create_mcp_server


@pytest.mark.asyncio
async def test_mcp_tools_do_not_advertise_structured_output_schema() -> None:
    server = create_mcp_server()

    tools = await server.list_tools()

    assert tools
    assert all(tool.outputSchema is None for tool in tools)
