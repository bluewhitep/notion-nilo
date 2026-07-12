import json

import pytest

from nilo.mcp_server.server import create_mcp_server
from nilo.mcp_server.tools import raw_api


class FakeRawApiService:
    # --------------------------------
    # Function Description:
    # Initializes an in-memory Raw API call recorder.
    # Inputs/Outputs:
    # No input; stores recorded operation calls.
    # Usage:
    # service = FakeRawApiService()
    # --------------------------------
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    # --------------------------------
    # Function Description:
    # Records one Raw API invocation without contacting Notion.
    # Inputs/Outputs:
    # Input operation and arguments; returns a structured echo payload.
    # Usage:
    # service.invoke("pages.retrieve", {"page_id": "page-1"})
    # --------------------------------
    def invoke(self, operation: str, arguments: dict[str, object]) -> dict[str, object]:
        self.calls.append((operation, arguments))
        return {"operation": operation, "arguments": arguments}


def text_result_to_json(result) -> dict[str, object]:
    assert result
    return json.loads(result[0].text)


@pytest.mark.asyncio
async def test_destructive_tools_are_annotated_and_require_confirmation() -> None:
    server = create_mcp_server()
    tools = {tool.name: tool for tool in await server.list_tools()}

    for name in ["page_trash", "block_trash"]:
        assert tools[name].annotations is not None
        assert tools[name].annotations.destructiveHint is True
        assert "confirm" in tools[name].inputSchema.get("required", [])


@pytest.mark.asyncio
async def test_destructive_tool_without_confirm_returns_error() -> None:
    result = await create_mcp_server().call_tool("page_trash", {"page_id": "page-1"})

    payload = text_result_to_json(result)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "confirmation_required"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("operation", "arguments"),
    [
        ("blocks.delete", {"block_id": "block-1"}),
        ("pages.update", {"page_id": "page-1", "in_trash": True}),
        ("databases.update", {"database_id": "database-1", "archived": True}),
    ],
)
# --------------------------------
# Function Description:
# Verifies delete, archive, and trash Raw API calls require explicit confirmation.
# Inputs/Outputs:
# Input fixtures and parametrized raw call; assertion-only async test.
# Usage:
# pytest tests/v2/mcp_server/test_dangerous_tools.py -k destructive_raw
# --------------------------------
async def test_destructive_raw_api_calls_require_confirmation(monkeypatch, operation, arguments) -> None:
    service = FakeRawApiService()
    monkeypatch.setattr(raw_api, "get_raw_api_service", lambda: service)

    result = await create_mcp_server().call_tool(
        "raw_api_invoke",
        {"operation": operation, "arguments": arguments},
    )

    payload = text_result_to_json(result)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "confirmation_required"
    assert service.calls == []


@pytest.mark.asyncio
# --------------------------------
# Function Description:
# Verifies registered read-only Raw API calls remain usable without confirmation.
# Inputs/Outputs:
# Input monkeypatch fixture; assertion-only async test.
# Usage:
# pytest tests/v2/mcp_server/test_dangerous_tools.py -k safe_calls
# --------------------------------
async def test_raw_api_safe_calls_do_not_require_confirmation(monkeypatch) -> None:
    service = FakeRawApiService()
    monkeypatch.setattr(raw_api, "get_raw_api_service", lambda: service)

    result = await create_mcp_server().call_tool(
        "raw_api_invoke",
        {"operation": "pages.retrieve", "arguments": {"page_id": "page-1"}},
    )

    assert text_result_to_json(result)["operation"] == "pages.retrieve"
    assert service.calls == [("pages.retrieve", {"page_id": "page-1"})]


@pytest.mark.asyncio
# --------------------------------
# Function Description:
# Verifies a confirmed destructive Raw API call reaches the shared Core service.
# Inputs/Outputs:
# Input monkeypatch fixture; assertion-only async test.
# Usage:
# pytest tests/v2/mcp_server/test_dangerous_tools.py -k confirmed_destructive
# --------------------------------
async def test_confirmed_destructive_raw_api_call_reaches_core(monkeypatch) -> None:
    service = FakeRawApiService()
    monkeypatch.setattr(raw_api, "get_raw_api_service", lambda: service)
    arguments = {"block_id": "block-1"}

    result = await create_mcp_server().call_tool(
        "raw_api_invoke",
        {"operation": "blocks.delete", "arguments": arguments, "confirm": True},
    )

    assert text_result_to_json(result)["operation"] == "blocks.delete"
    assert service.calls == [("blocks.delete", arguments)]
