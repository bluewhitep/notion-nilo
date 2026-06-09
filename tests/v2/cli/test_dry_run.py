import json

from typer.testing import CliRunner

from notion_mcp.cli import app
from notion_mcp.cli.commands import pages


runner = CliRunner()


class FakePagesService:
    def __init__(self) -> None:
        self.create_called = False

    def create(self, payload: dict[str, object]) -> dict[str, object]:
        self.create_called = True
        return {"created": payload}


def test_page_create_dry_run_does_not_call_core_write(monkeypatch) -> None:
    service = FakePagesService()
    monkeypatch.setattr(pages, "get_pages_service", lambda: service)

    result = runner.invoke(
        app,
        [
            "page",
            "create",
            "--payload",
            '{"parent": {"page_id": "root"}}',
            "--dry-run",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["dry_run"] is True
    assert payload["operation"] == "pages.create"
    assert service.create_called is False


def test_server_run_help_is_available() -> None:
    result = runner.invoke(app, ["server", "run", "--help"])

    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "--host" in result.stdout
    assert "--port" in result.stdout
