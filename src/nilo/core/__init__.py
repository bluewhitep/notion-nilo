# File: src/nilo/core/__init__.py
# Format: UTF-8
# =============================
# File Description:
# Core package exports the shared business layer used by CLI and MCP entrypoints.
# TAG: core, package
# =============================

from .config import (
    CoreConfig,
    DEFAULT_NOTION_VERSION,
    load_core_config,
    load_global_core_config,
    resolve_config_locations,
)
from .errors import CoreError
from .project import ConfigLocations

__all__ = [
    "ConfigLocations",
    "CoreConfig",
    "CoreError",
    "DEFAULT_NOTION_VERSION",
    "load_core_config",
    "load_global_core_config",
    "resolve_config_locations",
]
