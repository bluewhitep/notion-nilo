from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def read_doc(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_developer_and_user_doc_entrypoints_are_split() -> None:
    """Developer docs and user docs must expose separate MCP-oriented entrypoints."""
    assert (REPO_ROOT / "Docs" / "Developer").is_dir()
    assert (REPO_ROOT / "Docs" / "User").is_dir()
    assert (REPO_ROOT / "Docs" / "Developer" / "mcp_tools").is_dir()
    assert (REPO_ROOT / "Docs" / "User" / "MCP_Clients.md").is_file()


def test_architecture_documents_mcp_server_as_primary_entry() -> None:
    """Developer architecture docs must present MCP server lifecycle as the primary server entry."""
    architecture = read_doc("Docs/Developer/architecture/overview.md")

    assert "Core" in architecture
    assert "CLI" in architecture
    assert "MCP Tool" in architecture
    assert "notion-mcp server run" in architecture
    assert "notion-mcp server stdio" in architecture


def test_design_documents_core_cli_mcp_call_boundaries() -> None:
    """Architecture docs must state that CLI and MCP both call Core."""
    design = read_doc("Docs/Developer/architecture/overview.md")

    assert "Core" in design
    assert "CLI" in design
    assert "MCP Tool" in design
    assert "CLI -> Core" in design
    assert "MCP Tool -> Core" in design
    assert "MCP Tool -> CLI" not in design


def test_tech_stack_includes_uv_and_mcp_sdk() -> None:
    """Packaging docs must include uv and the MCP Python SDK as planned dependencies."""
    tech_stack = read_doc("Docs/Developer/packaging.md")

    assert "uv" in tech_stack
    assert "mcp" in tech_stack
    assert "MCP Python SDK" in tech_stack
    assert "Notion API version" in tech_stack


def test_public_docs_do_not_keep_old_top_level_planning_files() -> None:
    """Public Docs should not keep old top-level planning and private design files."""
    for relative_path in [
        "Docs/Requirements.md",
        "Docs/Design.md",
        "Docs/TechStack.md",
        "Docs/Development_Plan.md",
        "Docs/dev",
    ]:
        assert not (REPO_ROOT / relative_path).exists()
