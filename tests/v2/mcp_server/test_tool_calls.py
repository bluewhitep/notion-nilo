import json

import pytest

from nilo.mcp_server.server import create_mcp_server
from nilo.mcp_server.tools import config as config_tools
from nilo.mcp_server.tools import pages
from nilo.core.config import CoreConfig
from nilo.core.errors import ConfigValidationError


class FakePagesService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def retrieve(self, page_id: str) -> dict[str, object]:
        self.calls.append(("retrieve", page_id))
        return {"id": page_id, "object": "page"}

    def create(self, payload: dict[str, object]) -> dict[str, object]:
        self.calls.append(("create", payload))
        return {"created": payload}


def text_result_to_json(result) -> dict[str, object]:
    assert result
    return json.loads(result[0].text)


@pytest.mark.asyncio
async def test_page_retrieve_tool_calls_core_service(monkeypatch) -> None:
    service = FakePagesService()
    monkeypatch.setattr(pages, "get_pages_service", lambda: service)
    server = create_mcp_server()

    result = await server.call_tool("page_retrieve", {"page_id": "page-1"})

    assert text_result_to_json(result)["id"] == "page-1"
    assert service.calls == [("retrieve", "page-1")]


@pytest.mark.asyncio
async def test_page_create_dry_run_does_not_call_core_write(monkeypatch) -> None:
    service = FakePagesService()
    monkeypatch.setattr(pages, "get_pages_service", lambda: service)
    server = create_mcp_server()

    result = await server.call_tool(
        "page_create",
        {"payload": {"parent": {"page_id": "root"}}, "dry_run": True},
    )

    payload = text_result_to_json(result)
    assert payload["dry_run"] is True
    assert payload["operation"] == "pages.create"
    assert service.calls == []


@pytest.mark.asyncio
async def test_config_status_tool_returns_structured_result(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(tmp_path / "missing.json"))
    server = create_mcp_server()

    result = await server.call_tool("config_status", {})

    payload = text_result_to_json(result)
    assert payload["configured"] is False
    assert payload["capabilities"]["core"] is True


@pytest.mark.asyncio
async def test_config_status_tool_returns_core_error_for_invalid_config(monkeypatch) -> None:
    def invalid_config():
        raise ConfigValidationError("invalid test config")

    monkeypatch.setattr(config_tools, "load_core_config", invalid_config)

    result = await create_mcp_server().call_tool("config_status", {})

    payload = text_result_to_json(result)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "ConfigValidationError"
    assert payload["error"]["code"] == "config_validation_failed"


@pytest.mark.asyncio
# --------------------------------
# Function Description:
# Verifies Agent-facing MCP configuration reads cannot expose the Notion token.
# Inputs/Outputs:
# Input monkeypatch fixture; assertion-only async test.
# Usage:
# pytest tests/v2/mcp_server/test_tool_calls.py -k always_redacts
# --------------------------------
async def test_config_get_always_redacts_token_and_has_no_secret_override(monkeypatch) -> None:
    monkeypatch.setattr(config_tools, "load_core_config", lambda: CoreConfig(notion_token="ntn_test_secret"))
    server = create_mcp_server()
    tools = {tool.name: tool for tool in await server.list_tools()}

    result = await server.call_tool("config_get", {"key": "notion_token"})

    assert "show_secret" not in tools["config_get"].inputSchema.get("properties", {})
    assert text_result_to_json(result) == {"key": "notion_token", "value": "********"}
    assert "ntn_test_secret" not in result[0].text
