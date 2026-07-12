import json
import uuid
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nilo.cli import app
from nilo.core.config import (
    CoreConfig,
    init_core_config,
    load_core_config,
    load_global_core_config,
    save_core_config,
)
from nilo.core.project import ProjectConfigStore, ProjectSettings


runner = CliRunner()


def test_config_get_set_unset_and_list_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_file = tmp_path / "config.json"
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(cfg_file))
    init_core_config(
        notion_token="secret-token",
        user_name="Ada",
        user_id=str(uuid.uuid4()),
    )

    set_result = runner.invoke(app, ["config", "set", "user_name", "Grace"])
    assert set_result.exit_code == 0
    assert load_core_config().user_name == "Grace"

    get_result = runner.invoke(app, ["config", "get", "user_name", "--json"])
    assert get_result.exit_code == 0
    assert json.loads(get_result.stdout) == {"key": "user_name", "value": "Grace"}

    token_result = runner.invoke(app, ["config", "get", "notion_token", "--json"])
    assert token_result.exit_code == 0
    assert "secret-token" not in token_result.stdout
    assert json.loads(token_result.stdout)["value"] == "********"

    list_result = runner.invoke(app, ["config", "list", "--json"])
    assert list_result.exit_code == 0
    listed = json.loads(list_result.stdout)
    assert listed["notion_token_set"] is True
    assert listed["notion_token"] == "********"

    unset_result = runner.invoke(app, ["config", "unset", "user_name"])
    assert unset_result.exit_code == 0
    assert load_core_config().user_name is None


def test_config_rejects_unknown_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(tmp_path / "config.json"))

    result = runner.invoke(app, ["config", "set", "unknown", "value"])

    assert result.exit_code != 0
    assert "unknown" in result.stdout or "unknown" in str(result.exception)


def test_config_global_namespace_targets_global_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_file = tmp_path / "config.json"
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(cfg_file))

    set_result = runner.invoke(app, ["config", "global", "set", "notion_token", "secret-token"])
    name_result = runner.invoke(app, ["config", "global", "set", "user_name", "Ada"])
    list_result = runner.invoke(app, ["config", "global", "list", "--json"])

    assert set_result.exit_code == 0
    assert name_result.exit_code == 0
    assert list_result.exit_code == 0
    cfg = load_core_config(path=cfg_file)
    assert cfg.notion_token == "secret-token"
    assert cfg.user_name == "Ada"
    listed = json.loads(list_result.stdout)
    assert listed["notion_token_set"] is True
    assert "secret-token" not in list_result.stdout


def test_config_local_namespace_targets_project_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    global_cfg_file = tmp_path / "global.json"
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(global_cfg_file))

    init_result = runner.invoke(app, ["config", "local", "init", "--project-name", "Demo", "--json"])
    status_result = runner.invoke(app, ["config", "local", "status", "--json"])
    root_result = runner.invoke(app, ["config", "local", "root", "--json"])

    assert init_result.exit_code == 0
    assert status_result.exit_code == 0
    assert root_result.exit_code == 0
    local_config = tmp_path / ".notion_mcp" / "config.json"
    assert local_config.exists()
    raw = local_config.read_text(encoding="utf-8")
    assert "notion_token" not in raw
    assert json.loads(status_result.stdout)["config"]["project_name"] == "Demo"
    assert json.loads(root_result.stdout)["project_root"] == str(tmp_path)
    assert not global_cfg_file.exists()


# --------------------------------
# Function Description:
# Verifies public global CLI reads and writes never persist effective project overrides.
# Inputs/Outputs:
# Uses conflicting global/project versions; asserts the global file retains its own value.
# Usage:
# pytest tests/v2/cli/test_config_commands.py -k project_overrides
# --------------------------------
def test_global_cli_does_not_persist_project_overrides(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    global_file = tmp_path / "global.json"
    save_core_config(
        CoreConfig(notion_token="secret", notion_version="2025-09-03"),
        path=global_file,
    )
    project = ProjectConfigStore.init_project(tmp_path)
    project.settings = ProjectSettings(notion_version="2026-03-11")
    ProjectConfigStore.save(tmp_path, project)
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(global_file))
    monkeypatch.chdir(tmp_path)

    update = runner.invoke(app, ["config", "--global", "user.name", "Ada", "--json"])
    show = runner.invoke(app, ["config", "--global", "--show", "--json"])

    assert update.exit_code == 0
    assert show.exit_code == 0
    stored = load_global_core_config(path=global_file)
    assert stored.user_name == "Ada"
    assert stored.notion_version == "2025-09-03"
    assert json.loads(show.stdout)["notion_version"] == "2025-09-03"
