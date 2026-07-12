# File: src/nilo/config.py
# Format: UTF-8
# =============================
# File Description:
# Legacy configuration API delegating persistence and validation to Core.
# TAG: compatibility, config, core
# =============================

from __future__ import annotations

from pathlib import Path

from nilo.core.config import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_CONFIG_FILE,
    CoreConfig,
    config_path_from_env,
    load_global_core_config,
    save_core_config,
    update_core_config,
)
from nilo.core.errors import ConfigNotFoundError

Config = CoreConfig


# --------------------------------
# Function Description:
# Returns the Core-owned global configuration file path.
# Inputs/Outputs:
# No input; returns a filesystem Path.
# Usage:
# get_config_path()
# --------------------------------
def get_config_path() -> Path:
    return config_path_from_env()


# --------------------------------
# Function Description:
# Loads configuration through Core while preserving the legacy missing-file exception.
# Inputs/Outputs:
# Optional path; returns CoreConfig or raises FileNotFoundError when absent.
# Usage:
# load_config(path=Path("config.json"))
# --------------------------------
def load_config(path: Path | None = None) -> Config:
    try:
        return load_global_core_config(path=path)
    except ConfigNotFoundError as exc:
        raise FileNotFoundError(str(exc)) from exc


# --------------------------------
# Function Description:
# Saves configuration through the Core persistence contract.
# Inputs/Outputs:
# Input CoreConfig and optional path; writes the configuration file.
# Usage:
# save_config(Config(notion_token="secret"))
# --------------------------------
def save_config(config: Config, path: Path | None = None) -> None:
    save_core_config(config, path=path)


# --------------------------------
# Function Description:
# Updates the Notion token through the Core configuration API.
# Inputs/Outputs:
# Input token and optional path; writes the merged Core configuration.
# Usage:
# set_token("secret")
# --------------------------------
def set_token(token: str, path: Path | None = None) -> None:
    update_core_config(path=path, notion_token=token)


# --------------------------------
# Function Description:
# Updates the Notion user UUID through the Core configuration API.
# Inputs/Outputs:
# Input UUID string and optional path; writes the merged Core configuration.
# Usage:
# set_user("00000000-0000-0000-0000-000000000000")
# --------------------------------
def set_user(user_id: str, path: Path | None = None) -> None:
    update_core_config(path=path, user_id=user_id)


__all__ = [
    "Config",
    "DEFAULT_CONFIG_DIR",
    "DEFAULT_CONFIG_FILE",
    "get_config_path",
    "load_config",
    "save_config",
    "set_token",
    "set_user",
]
