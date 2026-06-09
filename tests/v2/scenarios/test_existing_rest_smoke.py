from __future__ import annotations

from fastapi.testclient import TestClient

from notion_mcp.server import app


def test_legacy_fastapi_root_still_responds() -> None:
    """The internal REST prototype root route remains importable for compatibility tests."""
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Notion MCP server is running"}


def test_legacy_fastapi_openapi_includes_existing_routes() -> None:
    """The internal REST prototype route inventory remains stable for compatibility tests."""
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/databases/" in paths
    assert "/pages/{page_id}" in paths
    assert "/blocks/{block_id}/children" in paths
