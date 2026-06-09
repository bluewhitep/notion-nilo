from pathlib import Path

import pytest
from typer.testing import CliRunner

from notion_mcp.cli import app as cli_app
from notion_mcp.config import load_config
from notion_mcp.core.config import load_core_config


runner = CliRunner()


def test_config_global_set_creates_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg_file = tmp_path / "config.json"
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(cfg_file))
    result = runner.invoke(cli_app, ["config", "global", "set", "notion_token", "abc"])
    assert result.exit_code == 0
    cfg = load_config(path=cfg_file)
    assert cfg.notion_token == "abc"


def test_config_global_token_and_user_name_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg_file = tmp_path / "config.json"
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(cfg_file))

    result_token = runner.invoke(cli_app, ["config", "--global", "user.token", "newtoken"])
    assert result_token.exit_code == 0
    cfg = load_config(path=cfg_file)
    assert cfg.notion_token == "newtoken"
    result_user = runner.invoke(cli_app, ["config", "--global", "user.name", "Ada"])
    assert result_user.exit_code == 0
    cfg2 = load_core_config(path=cfg_file)
    assert cfg2.user_name == "Ada"


def test_removed_legacy_show_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """Legacy show command is no longer a public CLI entry."""
    runner = CliRunner()
    monkeypatch.setenv("NOTION_MCP_CONFIG", "/tmp/nonexistent/config.json")
    result = runner.invoke(cli_app, ["show"])
    assert result.exit_code != 0
