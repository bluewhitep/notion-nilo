# File: src/nilo/core/config.py
# Format: UTF-8
# =============================
# File Description:
# Global and effective project-aware configuration contracts for the Core layer.
# TAG: core, config, project
# =============================

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError, field_validator

from .config_constants import DEFAULT_TRANSPORT, SUPPORTED_TRANSPORTS
from .errors import ConfigNotFoundError, ConfigValidationError
from .project import ConfigLocations, ProjectConfigStore, ProjectResolver
from .project.project_paths import global_config_file

DEFAULT_CONFIG_DIR = Path.home() / ".notion_mcp"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
DEFAULT_NOTION_VERSION = "2026-03-11"


class CoreConfig(BaseModel):
    notion_token: str | None = Field(default=None)
    user_name: str | None = Field(default=None)
    user_id: str | None = Field(default=None)
    notion_version: str = Field(default=DEFAULT_NOTION_VERSION)
    timeout_ms: int = Field(default=60000, ge=1)
    retry: bool = Field(default=True)
    default_transport: str = Field(default=DEFAULT_TRANSPORT)
    audit_enabled: bool = Field(default=True)

    # --------------------------------
    # Function Description:
    # Initializes CoreConfig and converts Pydantic errors to Core errors.
    # Inputs/Outputs:
    # Input keyword configuration data; output is a validated config object.
    # Usage:
    # CoreConfig(notion_token="secret")
    # --------------------------------
    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except ValidationError as exc:
            fields = ", ".join(
                ".".join(str(part) for part in error.get("loc", ()))
                for error in exc.errors()
            )
            suffix = f": {fields}" if fields else ""
            raise ConfigValidationError(
                f"Invalid Core configuration{suffix}",
                details={"errors": exc.errors()},
            ) from exc

    # --------------------------------
    # Function Description:
    # Validates configured Notion user id values.
    # Inputs/Outputs:
    # Input optional string; output normalized UUID string or None.
    # Usage:
    # CoreConfig(user_id="00000000-0000-0000-0000-000000000000")
    # --------------------------------
    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        try:
            return str(UUID(value))
        except ValueError as exc:
            raise ValueError("user_id must be a Notion user UUID") from exc

    # --------------------------------
    # Function Description:
    # Validates that Notion API version is not blank.
    # Inputs/Outputs:
    # Input version string; output stripped version string.
    # Usage:
    # CoreConfig(notion_version="2026-03-11")
    # --------------------------------
    @field_validator("notion_version")
    @classmethod
    def validate_notion_version(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("notion_version cannot be empty")
        return stripped

    # --------------------------------
    # Function Description:
    # Validates the configured local transport against the Core whitelist.
    # Inputs/Outputs:
    # Input transport string; returns normalized stdio or streamable-http.
    # Usage:
    # CoreConfig(default_transport="stdio")
    # --------------------------------
    @field_validator("default_transport")
    @classmethod
    def validate_default_transport(cls, value: str) -> str:
        normalized = value.strip()
        if normalized not in SUPPORTED_TRANSPORTS:
            raise ValueError(
                "default_transport must be one of: "
                f"{', '.join(sorted(SUPPORTED_TRANSPORTS))}"
            )
        return normalized


# --------------------------------
# Function Description:
# Resolves the active Core config path from environment or default.
# Inputs/Outputs:
# No input; returns a filesystem Path.
# Usage:
# config_path_from_env()
# --------------------------------
def config_path_from_env() -> Path:
    return global_config_file()


# --------------------------------
# Function Description:
# Resolves existing project and global configuration directories for a start path.
# Inputs/Outputs:
# Input optional cwd/home paths; returns ConfigLocations with explicit Path or None values.
# Usage:
# resolve_config_locations(Path.cwd())
# --------------------------------
def resolve_config_locations(
    cwd: Path | None = None,
    *,
    home: Path | None = None,
) -> ConfigLocations:
    return ProjectResolver.resolve_config_locations(cwd, home=home)


# --------------------------------
# Function Description:
# Loads global Core configuration from disk without project-level overrides.
# Inputs/Outputs:
# Optional path input; returns CoreConfig or raises CoreError.
# Usage:
# load_global_core_config(path=Path("config.json"))
# --------------------------------
def load_global_core_config(path: Path | None = None) -> CoreConfig:
    cfg_path = path or config_path_from_env()
    if not cfg_path.exists():
        raise ConfigNotFoundError(str(cfg_path))
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigValidationError(
            "Configuration file is not valid JSON",
            details={"path": str(cfg_path)},
        ) from exc
    if not isinstance(data, dict):
        raise ConfigValidationError(
            "Configuration file must contain a JSON object",
            details={"path": str(cfg_path)},
        )
    return CoreConfig(**data)


# --------------------------------
# Function Description:
# Loads global Core config and applies credential-free project setting overrides.
# Inputs/Outputs:
# Optional explicit path/cwd/home; returns effective CoreConfig or raises CoreError.
# Usage:
# load_core_config(cwd=Path.cwd())
# --------------------------------
def load_core_config(
    path: Path | None = None,
    *,
    cwd: Path | None = None,
    home: Path | None = None,
) -> CoreConfig:
    global_path = path if path is not None else global_config_file(home)
    config = load_global_core_config(path=global_path)
    if path is not None:
        return config
    locations = resolve_config_locations(cwd, home=home)
    if locations.project_dir is None:
        return config
    project_config = ProjectConfigStore.load(locations.project_dir.parent)
    overrides = project_config.settings.core_overrides()
    if not overrides:
        return config
    return CoreConfig(**{**config.model_dump(), **overrides})


# --------------------------------
# Function Description:
# Saves Core configuration to disk with owner-only permissions.
# Inputs/Outputs:
# Input config and optional path; output is None after writing the file.
# Usage:
# save_core_config(CoreConfig(notion_token="secret"))
# --------------------------------
def save_core_config(config: CoreConfig, path: Path | None = None) -> None:
    cfg_path = path or config_path_from_env()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    payload = config.model_dump(exclude_none=True)
    cfg_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.chmod(cfg_path, 0o600)


# --------------------------------
# Function Description:
# Initializes the Core configuration file.
# Inputs/Outputs:
# Input token/user metadata and optional path; returns saved CoreConfig.
# Usage:
# init_core_config(notion_token="secret", user_name="Ada")
# --------------------------------
def init_core_config(
    *,
    notion_token: str,
    user_name: str,
    user_id: str | None = None,
    notion_version: str = DEFAULT_NOTION_VERSION,
    timeout_ms: int = 60000,
    retry: bool = True,
    default_transport: str = DEFAULT_TRANSPORT,
    path: Path | None = None,
) -> CoreConfig:
    config = CoreConfig(
        notion_token=notion_token,
        user_name=user_name,
        user_id=user_id,
        notion_version=notion_version,
        timeout_ms=timeout_ms,
        retry=retry,
        default_transport=default_transport,
    )
    save_core_config(config, path=path)
    return config


# --------------------------------
# Function Description:
# Updates selected Core configuration fields without clearing unspecified values.
# Inputs/Outputs:
# Input optional field values and path; returns the updated CoreConfig.
# Usage:
# update_core_config(notion_version="2026-03-11")
# --------------------------------
def update_core_config(
    *,
    path: Path | None = None,
    notion_token: str | None = None,
    user_name: str | None = None,
    user_id: str | None = None,
    notion_version: str | None = None,
    timeout_ms: int | None = None,
    retry: bool | None = None,
    default_transport: str | None = None,
    audit_enabled: bool | None = None,
) -> CoreConfig:
    try:
        config = load_global_core_config(path=path)
    except ConfigNotFoundError:
        config = CoreConfig()
    updates = {
        "notion_token": notion_token,
        "user_name": user_name,
        "user_id": user_id,
        "notion_version": notion_version,
        "timeout_ms": timeout_ms,
        "retry": retry,
        "default_transport": default_transport,
        "audit_enabled": audit_enabled,
    }
    current = config.model_dump()
    for key, value in updates.items():
        if value is not None:
            current[key] = value
    updated = CoreConfig(**current)
    save_core_config(updated, path=path)
    return updated


# --------------------------------
# Function Description:
# Produces a token-safe public configuration dictionary.
# Inputs/Outputs:
# Input CoreConfig; returns dictionary suitable for status output.
# Usage:
# redacted_config(config)
# --------------------------------
def redacted_config(config: CoreConfig) -> dict[str, Any]:
    public = config.model_dump(exclude={"notion_token"})
    public["notion_token_set"] = bool(config.notion_token)
    public["notion_token"] = "********" if config.notion_token else None
    return public
