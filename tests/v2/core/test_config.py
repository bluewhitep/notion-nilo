# File: tests/v2/core/test_config.py
# Format: UTF-8
# =============================
# File Description:
# Core tests for global, project-aware, and credential-safe configuration behavior.
# TAG: test, core, config, project
# =============================

import json
import stat
import uuid
from pathlib import Path

import pytest

from nilo.core import ConfigLocations as PublicConfigLocations
from nilo.core import resolve_config_locations as public_resolve_config_locations
from nilo.core.config import (
    DEFAULT_NOTION_VERSION,
    CoreConfig,
    config_path_from_env,
    init_core_config,
    load_core_config,
    load_global_core_config,
    redacted_config,
    resolve_config_locations,
    save_core_config,
    update_core_config,
)
from nilo.core.errors import ConfigNotFoundError, ConfigValidationError
from nilo.core.project import ProjectConfigStore, ProjectSettings


def test_init_core_config_writes_secure_file_and_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_file = tmp_path / "config.json"
    user_id = str(uuid.uuid4())
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(cfg_file))

    cfg = init_core_config(
        notion_token="secret-token",
        user_name="Ada",
        user_id=user_id,
    )

    assert cfg.notion_token == "secret-token"
    assert cfg.user_name == "Ada"
    assert cfg.user_id == user_id
    assert cfg.notion_version == DEFAULT_NOTION_VERSION
    assert cfg.default_transport == "stdio"
    assert cfg_file.exists()
    assert stat.S_IMODE(cfg_file.stat().st_mode) == 0o600

    stored = json.loads(cfg_file.read_text(encoding="utf-8"))
    assert stored["notion_token"] == "secret-token"
    assert stored["user_name"] == "Ada"
    assert stored["user_id"] == user_id
    assert stored["notion_version"] == DEFAULT_NOTION_VERSION


def test_load_update_and_path_override(tmp_path: Path) -> None:
    cfg_file = tmp_path / "custom" / "config.json"
    user_id = str(uuid.uuid4())
    save_core_config(
        CoreConfig(
            notion_token="token-a",
            user_name="Ada",
            user_id=user_id,
        ),
        path=cfg_file,
    )

    updated = update_core_config(
        path=cfg_file,
        notion_version="2025-09-03",
        timeout_ms=12345,
        retry=False,
    )

    assert updated.notion_token == "token-a"
    assert updated.user_name == "Ada"
    assert updated.user_id == user_id
    assert updated.notion_version == "2025-09-03"
    assert updated.timeout_ms == 12345
    assert updated.retry is False
    assert load_core_config(path=cfg_file).timeout_ms == 12345


def test_config_path_from_env_expands_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOTION_MCP_CONFIG", "~/notion-test-config.json")

    assert config_path_from_env().name == "notion-test-config.json"
    assert str(config_path_from_env()).startswith(str(Path.home()))


def test_redacted_config_never_leaks_token() -> None:
    cfg = CoreConfig(
        notion_token="secret-token",
        user_name="Ada",
        user_id=str(uuid.uuid4()),
    )

    public = redacted_config(cfg)

    assert "secret-token" not in json.dumps(public)
    assert public["notion_token_set"] is True
    assert public["notion_token"] == "********"
    assert public["user_name"] == "Ada"


def test_user_id_must_be_uuid() -> None:
    with pytest.raises(ConfigValidationError):
        CoreConfig(
            notion_token="secret-token",
            user_name="Ada",
            user_id="not-a-uuid",
        )


# --------------------------------
# Function Description:
# Verifies project-safe settings override global values without replacing credentials.
# Inputs/Outputs:
# Uses temporary global/project files; asserts the effective CoreConfig field precedence.
# Usage:
# pytest tests/v2/core/test_config.py -k project_settings_override
# --------------------------------
def test_project_settings_override_global_non_sensitive_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    global_file = home / ".notion_mcp" / "config.json"
    project_root = home / "work" / "demo"
    child = project_root / "src"
    monkeypatch.delenv("NOTION_MCP_CONFIG", raising=False)
    save_core_config(
        CoreConfig(
            notion_token="global-secret",
            user_name="Global User",
            user_id=str(uuid.uuid4()),
            notion_version="2025-09-03",
            timeout_ms=1000,
            retry=True,
            default_transport="stdio",
            audit_enabled=True,
        ),
        path=global_file,
    )
    project = ProjectConfigStore.init_project(project_root, project_name="Demo")
    project.settings = ProjectSettings(
        notion_version="2026-03-11",
        timeout_ms=2500,
        retry=False,
        default_transport="streamable-http",
        audit_enabled=False,
    )
    ProjectConfigStore.save(project_root, project)
    child.mkdir(parents=True)

    effective = load_core_config(cwd=child, home=home)

    assert effective.notion_token == "global-secret"
    assert effective.user_name == "Global User"
    assert effective.user_id is not None
    assert effective.notion_version == "2026-03-11"
    assert effective.timeout_ms == 2500
    assert effective.retry is False
    assert effective.default_transport == "streamable-http"
    assert effective.audit_enabled is False
    assert load_global_core_config(path=global_file).notion_version == "2025-09-03"


# --------------------------------
# Function Description:
# Verifies an explicit Core config path bypasses project-level overrides.
# Inputs/Outputs:
# Uses explicit path/cwd inputs; asserts the returned values remain global-only.
# Usage:
# pytest tests/v2/core/test_config.py -k explicit_config_path
# --------------------------------
def test_explicit_config_path_does_not_apply_project_overrides(tmp_path: Path) -> None:
    home = tmp_path / "home"
    global_file = home / ".notion_mcp" / "config.json"
    project_root = home / "work" / "demo"
    save_core_config(CoreConfig(notion_token="secret", retry=True), path=global_file)
    project = ProjectConfigStore.init_project(project_root)
    project.settings = ProjectSettings(retry=False)
    ProjectConfigStore.save(project_root, project)

    loaded = load_core_config(path=global_file, cwd=project_root, home=home)

    assert loaded.retry is True


# --------------------------------
# Function Description:
# Verifies project settings cannot make a missing global credential config optional.
# Inputs/Outputs:
# Uses a project with no global file; asserts ConfigNotFoundError remains the contract.
# Usage:
# pytest tests/v2/core/test_config.py -k requires_global
# --------------------------------
def test_effective_config_still_requires_global_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    project_root = home / "work" / "demo"
    monkeypatch.delenv("NOTION_MCP_CONFIG", raising=False)
    ProjectConfigStore.init_project(project_root)

    with pytest.raises(ConfigNotFoundError):
        load_core_config(cwd=project_root, home=home)


# --------------------------------
# Function Description:
# Verifies the public location interface reports only existing configuration directories.
# Inputs/Outputs:
# Uses an empty home; returns project_dir=None and global_dir=None.
# Usage:
# pytest tests/v2/core/test_config.py -k location_interface
# --------------------------------
def test_config_location_interface_returns_none_for_missing_locations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    child = home / "work" / "demo"
    child.mkdir(parents=True)
    monkeypatch.delenv("NOTION_MCP_CONFIG", raising=False)

    locations = resolve_config_locations(child, home=home)

    assert locations.project_dir is None
    assert locations.global_dir is None
    assert isinstance(locations, PublicConfigLocations)
    assert public_resolve_config_locations(child, home=home) == locations


# --------------------------------
# Function Description:
# Verifies Core configuration rejects the unsupported legacy SSE transport.
# Inputs/Outputs:
# Constructs CoreConfig with sse; asserts ConfigValidationError.
# Usage:
# pytest tests/v2/core/test_config.py -k legacy_sse
# --------------------------------
def test_core_config_rejects_legacy_sse_transport() -> None:
    with pytest.raises(ConfigValidationError):
        CoreConfig(default_transport="sse")
