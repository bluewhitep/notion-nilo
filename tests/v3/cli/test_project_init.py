# File: tests/v3/cli/test_project_init.py
# Format: UTF-8
# =============================
# File Description:
# CLI tests for project initialization, credential isolation, and root ignore hygiene.
# TAG: test, cli, project, init, gitignore
# =============================

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nilo.cli import app


runner = CliRunner()


def test_project_init_creates_project_config_without_tokens(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["project", "init", "--project-name", "Demo", "--workspace-hint", "Sandbox"])

    assert result.exit_code == 0
    assert "Created .notion_mcp/" in result.stdout
    assert "does not store Notion tokens" in result.stdout

    project_dir = tmp_path / ".notion_mcp"
    config_file = project_dir / "config.json"
    assert config_file.exists()
    assert (project_dir / "state").is_dir()
    assert (project_dir / "cache").is_dir()
    assert (project_dir / "logs").is_dir()
    assert (project_dir / ".gitignore").read_text(encoding="utf-8") == "state/\ncache/\nlogs/\n"

    raw = config_file.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert data["schema_version"] == 1
    assert data["project_name"] == "Demo"
    assert data["workspace_hint"] == "Sandbox"
    assert data["settings"]["prefer_attached_page"] is True
    assert data["settings"]["prefer_attached_database"] is True
    assert "notion_token" not in data
    assert "token" not in raw.lower()


def test_project_init_rejects_existing_config_without_force(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    first = runner.invoke(app, ["project", "init", "--project-name", "First"])
    assert first.exit_code == 0

    second = runner.invoke(app, ["project", "init", "--project-name", "Second"])

    assert second.exit_code == 1
    assert "Project already initialized" in second.stdout
    data = json.loads((tmp_path / ".notion_mcp" / "config.json").read_text(encoding="utf-8"))
    assert data["project_name"] == "First"


def test_project_init_force_overwrites_existing_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    first = runner.invoke(app, ["project", "init", "--project-name", "First"])
    assert first.exit_code == 0

    forced = runner.invoke(app, ["project", "init", "--project-name", "Second", "--force", "--json"])

    assert forced.exit_code == 0
    payload = json.loads(forced.stdout)
    assert payload["ok"] is True
    assert payload["project_root"] == str(tmp_path)
    data = json.loads((tmp_path / ".notion_mcp" / "config.json").read_text(encoding="utf-8"))
    assert data["project_name"] == "Second"


def test_local_init_alias_uses_project_init_behavior(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["local", "init", "--project-name", "Alias"])

    assert result.exit_code == 0
    data = json.loads((tmp_path / ".notion_mcp" / "config.json").read_text(encoding="utf-8"))
    assert data["project_name"] == "Alias"


# --------------------------------
# Function Description:
# Verifies CLI project init creates and idempotently maintains the root ignore entry.
# Inputs/Outputs:
# Invokes init and forced init; asserts one .notion_mcp/ line in root .gitignore.
# Usage:
# pytest tests/v3/cli/test_project_init.py -k root_gitignore
# --------------------------------
def test_project_init_creates_root_gitignore_entry_idempotently(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    first = runner.invoke(app, ["project", "init"])
    forced = runner.invoke(app, ["project", "init", "--force"])

    assert first.exit_code == 0
    assert forced.exit_code == 0
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8") == ".notion_mcp/\n"
