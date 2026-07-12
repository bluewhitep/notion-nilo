# File: tests/v3/core/test_project_resolver.py
# Format: UTF-8
# =============================
# File Description:
# Core tests for bounded project discovery, configuration locations, and project initialization.
# TAG: test, core, project, config, resolver
# =============================

import json
from pathlib import Path

import pytest

from nilo.core.errors import ProjectConfigNotFoundError, ProjectConfigValidationError
from nilo.core.project import ProjectConfigStore, ProjectResolver


def test_project_resolver_finds_project_root_from_child_directory(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "my-project"
    child = root / "src" / "module"
    child.mkdir(parents=True)
    ProjectConfigStore.init_project(root, project_name="Demo")

    assert ProjectResolver.find_project_root(child) == root
    assert ProjectResolver.find_project_config(child) == root / ".notion_mcp" / "config.json"


def test_project_resolver_returns_clear_error_when_config_is_missing(tmp_path: Path) -> None:
    child = tmp_path / "missing" / "child"
    child.mkdir(parents=True)

    with pytest.raises(ProjectConfigNotFoundError) as exc_info:
        ProjectResolver.find_project_root(child)

    assert ".notion_mcp/config.json" in exc_info.value.message
    assert str(child) in exc_info.value.details["start"]


def test_project_config_store_initializes_expected_directory_shape(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    config = ProjectConfigStore.init_project(
        project_root,
        project_name="Demo",
        workspace_hint="Sandbox",
    )

    project_dir = project_root / ".notion_mcp"
    config_file = project_dir / "config.json"
    assert config.schema_version == 1
    assert config.project_name == "Demo"
    assert config.workspace_hint == "Sandbox"
    assert config_file.exists()
    assert (project_dir / "state").is_dir()
    assert (project_dir / "cache").is_dir()
    assert (project_dir / "logs").is_dir()
    assert (project_dir / ".gitignore").read_text(encoding="utf-8") == "state/\ncache/\nlogs/\n"

    raw_config = json.loads(config_file.read_text(encoding="utf-8"))
    assert raw_config["settings"]["prefer_attached_page"] is True
    assert raw_config["settings"]["prefer_attached_database"] is True
    assert raw_config["settings"]["json_output_default"] is False
    assert "notion_token" not in raw_config
    assert "token" not in config_file.read_text(encoding="utf-8").lower()


def test_project_config_store_rejects_token_fields(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    config_file = project_root / ".notion_mcp" / "config.json"
    config_file.parent.mkdir(parents=True)
    config_file.write_text('{"schema_version": 1, "notion_token": "secret"}\n', encoding="utf-8")

    with pytest.raises(ValueError) as exc_info:
        ProjectConfigStore.load(project_root)

    assert "token" in str(exc_info.value)


# --------------------------------
# Function Description:
# Verifies location discovery returns both the nearest project and existing global directories.
# Inputs/Outputs:
# Uses a nested project below a temporary home; asserts both absolute directory paths.
# Usage:
# pytest tests/v3/core/test_project_resolver.py -k returns_project_and_global
# --------------------------------
def test_config_locations_return_project_and_global_directories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    global_dir = home / ".notion_mcp"
    global_dir.mkdir(parents=True)
    (global_dir / "config.json").write_text("{}\n", encoding="utf-8")
    project_root = home / "work" / "demo"
    child = project_root / "src" / "module"
    ProjectConfigStore.init_project(project_root)
    child.mkdir(parents=True)
    monkeypatch.delenv("NOTION_MCP_CONFIG", raising=False)

    locations = ProjectResolver.resolve_config_locations(child, home=home)

    assert locations.project_dir == project_root / ".notion_mcp"
    assert locations.global_dir == global_dir


# --------------------------------
# Function Description:
# Verifies home-level .notion_mcp is global-only and never a project root.
# Inputs/Outputs:
# Uses a home global config and nested cwd; returns no project and raises on project lookup.
# Usage:
# pytest tests/v3/core/test_project_resolver.py -k home_config_is_global_only
# --------------------------------
def test_home_config_is_global_only_for_upward_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    global_dir = home / ".notion_mcp"
    child = home / "workspace" / "nested"
    global_dir.mkdir(parents=True)
    child.mkdir(parents=True)
    (global_dir / "config.json").write_text("{}\n", encoding="utf-8")
    monkeypatch.delenv("NOTION_MCP_CONFIG", raising=False)

    locations = ProjectResolver.resolve_config_locations(child, home=home)

    assert locations.project_dir is None
    assert locations.global_dir == global_dir
    with pytest.raises(ProjectConfigNotFoundError):
        ProjectResolver.find_project_root(child, home=home)


# --------------------------------
# Function Description:
# Verifies Git-like project lookup remains usable when a workspace is outside the home tree.
# Inputs/Outputs:
# Uses disjoint home/workspace paths; finds the project while global lookup remains home-scoped.
# Usage:
# pytest tests/v3/core/test_project_resolver.py -k outside_home
# --------------------------------
def test_project_lookup_outside_home_stops_at_filesystem_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    project_root = tmp_path / "external" / "demo"
    child = project_root / "src"
    home.mkdir()
    ProjectConfigStore.init_project(project_root, home=home)
    child.mkdir()
    monkeypatch.delenv("NOTION_MCP_CONFIG", raising=False)

    locations = ProjectResolver.resolve_config_locations(child, home=home)

    assert locations.project_dir == project_root / ".notion_mcp"
    assert locations.global_dir is None


# --------------------------------
# Function Description:
# Verifies an existing NOTION_MCP_CONFIG file defines the reported global directory.
# Inputs/Outputs:
# Uses environment and home config files; asserts the environment file parent wins.
# Usage:
# pytest tests/v3/core/test_project_resolver.py -k environment_global
# --------------------------------
def test_environment_global_config_location_takes_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    home_global = home / ".notion_mcp" / "config.json"
    env_global = tmp_path / "custom-global" / "nilo.json"
    home_global.parent.mkdir(parents=True)
    env_global.parent.mkdir(parents=True)
    home_global.write_text("{}\n", encoding="utf-8")
    env_global.write_text("{}\n", encoding="utf-8")
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(env_global))

    locations = ProjectResolver.resolve_config_locations(home, home=home)

    assert locations.project_dir is None
    assert locations.global_dir == env_global.parent


# --------------------------------
# Function Description:
# Verifies project init preserves root ignore content and adds its entry once.
# Inputs/Outputs:
# Initializes twice with force; asserts stable incremental .gitignore content.
# Usage:
# pytest tests/v3/core/test_project_resolver.py -k preserves_root_gitignore
# --------------------------------
def test_project_init_preserves_root_gitignore_and_adds_entry_once(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    root_gitignore = project_root / ".gitignore"
    root_gitignore.write_text("dist/\n# keep this comment", encoding="utf-8")

    ProjectConfigStore.init_project(project_root)
    first_content = root_gitignore.read_text(encoding="utf-8")
    ProjectConfigStore.init_project(project_root, force=True)

    assert first_content == "dist/\n# keep this comment\n.notion_mcp/\n"
    assert root_gitignore.read_text(encoding="utf-8") == first_content


# --------------------------------
# Function Description:
# Verifies both Store and Resolver initialization reject the reserved user home.
# Inputs/Outputs:
# Uses an injected temporary home; asserts ProjectConfigValidationError and no project files.
# Usage:
# pytest tests/v3/core/test_project_resolver.py -k rejects_user_home
# --------------------------------
def test_project_initialization_rejects_user_home(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()

    with pytest.raises(ProjectConfigValidationError):
        ProjectConfigStore.init_project(home, home=home)
    with pytest.raises(ProjectConfigValidationError):
        ProjectResolver.init_project(home, home=home)

    assert not (home / ".notion_mcp").exists()
    assert not (home / ".gitignore").exists()


# --------------------------------
# Function Description:
# Verifies project configuration rejects a legacy SSE transport override.
# Inputs/Outputs:
# Mutates a temporary project config; asserts ProjectConfigValidationError on load.
# Usage:
# pytest tests/v3/core/test_project_resolver.py -k legacy_sse
# --------------------------------
def test_project_config_rejects_legacy_sse_transport(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    ProjectConfigStore.init_project(project_root)
    config_file = project_root / ".notion_mcp" / "config.json"
    raw = json.loads(config_file.read_text(encoding="utf-8"))
    raw["settings"]["default_transport"] = "sse"
    config_file.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ProjectConfigValidationError):
        ProjectConfigStore.load(project_root)
