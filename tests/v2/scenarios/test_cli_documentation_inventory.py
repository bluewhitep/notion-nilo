from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def read_user_cli_docs() -> str:
    paths = [
        REPO_ROOT / "Docs/User/Cli.md",
        *sorted((REPO_ROOT / "Docs/User/Cli").glob("*.md")),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_user_cli_doc_lists_all_current_cli_commands() -> None:
    text = read_user_cli_docs()

    required_commands = [
        "notion-mcp init",
        "notion-mcp pwd",
        "notion-mcp version",
        "notion-mcp config --global --show",
        "notion-mcp config --local --show",
        "notion-mcp config --global user.token",
        "notion-mcp config --global user.name",
        "notion-mcp auth validate",
        "notion-mcp auth whoami",
        "notion-mcp page attach",
        "notion-mcp page status",
        "notion-mcp page refresh",
        "notion-mcp page detach",
        "notion-mcp page retrieve",
        "notion-mcp page blocks",
        "notion-mcp page create",
        "notion-mcp page update",
        "notion-mcp page trash",
        "notion-mcp block children",
        "notion-mcp block append",
        "notion-mcp block insert-after",
        "notion-mcp block update",
        "notion-mcp block trash",
        "notion-mcp database attach",
        "notion-mcp database status",
        "notion-mcp database refresh",
        "notion-mcp database detach",
        "notion-mcp database retrieve",
        "notion-mcp database sources",
        "notion-mcp database create",
        "notion-mcp database update",
        "notion-mcp database rename",
        "notion-mcp database query",
        "notion-mcp database page create",
        "notion-mcp database property rename",
        "notion-mcp data-source retrieve",
        "notion-mcp data-source query",
        "notion-mcp data-source create",
        "notion-mcp data-source update",
        "notion-mcp data-source templates",
        "notion-mcp data-source property rename",
        "notion-mcp data-source page create",
        "notion-mcp user me",
        "notion-mcp user list",
        "notion-mcp user retrieve",
        "notion-mcp comment list",
        "notion-mcp comment create",
        "notion-mcp comment reply",
        "notion-mcp view retrieve",
        "notion-mcp view list",
        "notion-mcp view query",
        "notion-mcp view create",
        "notion-mcp view update",
        "notion-mcp file-upload retrieve",
        "notion-mcp file-upload list",
        "notion-mcp file-upload create",
        "notion-mcp file-upload send",
        "notion-mcp file-upload complete",
        "notion-mcp search query",
        "notion-mcp custom-emoji list",
        "notion-mcp custom-emoji retrieve",
        "notion-mcp raw-api operations",
        "notion-mcp raw-api invoke",
        "notion-mcp server run",
        "notion-mcp server status",
        "notion-mcp server stop",
        "notion-mcp server logs",
        "notion-mcp server remove",
        "notion-mcp server stdio",
    ]

    for command in required_commands:
        assert command in text, command


def test_user_cli_doc_positions_raw_api_as_advanced_fallback() -> None:
    text = read_user_cli_docs()

    assert "Raw API 只作为高级兜底入口" in text
    assert "notion-mcp raw-api operations" in text
    assert "notion-mcp raw-api invoke" in text
