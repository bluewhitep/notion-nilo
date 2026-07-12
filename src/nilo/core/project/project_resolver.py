# File: src/nilo/core/project/project_resolver.py
# Format: UTF-8
# =============================
# File Description:
# Git-like resolver for project and global .notion_mcp configuration locations.
# TAG: core, project, config, resolver
# =============================

from __future__ import annotations

from pathlib import Path

from nilo.core.errors import ProjectConfigNotFoundError

from .project_config import ProjectConfig, ProjectConfigStore
from .project_paths import ConfigLocations, ProjectPaths, global_config_file, normalize_path


# --------------------------------
# Function Description:
# Normalizes a start path to the directory used for upward configuration lookup.
# Inputs/Outputs:
# Input optional path; returns an absolute directory path.
# Usage:
# normalize_start_path(Path.cwd())
# --------------------------------
def normalize_start_path(cwd: Path | None = None) -> Path:
    start = Path.cwd() if cwd is None else Path(cwd)
    current = normalize_path(start)
    return current.parent if current.is_file() else current


# --------------------------------
# Function Description:
# Finds the nearest project root without treating the user home or filesystem root as a project.
# Inputs/Outputs:
# Input start/home; bounds an in-home search at home and an external search at its filesystem root.
# Usage:
# find_project_root_or_none(Path.cwd(), Path.home())
# --------------------------------
def find_project_root_or_none(start: Path, home: Path) -> Path | None:
    boundary = home if start == home or home in start.parents else Path(start.anchor)
    for candidate in (start, *start.parents):
        if candidate == boundary:
            break
        if ProjectPaths(candidate).config_file.is_file():
            return candidate
    return None


class ProjectResolver:
    # --------------------------------
    # Function Description:
    # Resolves existing project and global configuration directories.
    # Inputs/Outputs:
    # Input optional start/home paths; returns ConfigLocations with Path or None fields.
    # Usage:
    # ProjectResolver.resolve_config_locations(Path.cwd())
    # --------------------------------
    @staticmethod
    def resolve_config_locations(
        cwd: Path | None = None,
        *,
        home: Path | None = None,
    ) -> ConfigLocations:
        current = normalize_start_path(cwd)
        home_dir = normalize_path(Path.home() if home is None else Path(home))
        project_root = find_project_root_or_none(current, home_dir)
        global_file = global_config_file(home_dir)
        return ConfigLocations(
            project_dir=ProjectPaths(project_root).project_dir if project_root is not None else None,
            global_dir=global_file.expanduser().resolve().parent if global_file.is_file() else None,
        )

    # --------------------------------
    # Function Description:
    # Finds the nearest project below the user home containing .notion_mcp/config.json.
    # Inputs/Outputs:
    # Input optional start/home paths; returns project root or raises ProjectConfigNotFoundError.
    # Usage:
    # ProjectResolver.find_project_root(Path.cwd())
    # --------------------------------
    @staticmethod
    def find_project_root(
        cwd: Path | None = None,
        *,
        home: Path | None = None,
    ) -> Path:
        current = normalize_start_path(cwd)
        home_dir = normalize_path(Path.home() if home is None else Path(home))
        project_root = find_project_root_or_none(current, home_dir)
        if project_root is not None:
            return project_root
        raise ProjectConfigNotFoundError(str(current))

    # --------------------------------
    # Function Description:
    # Finds the nearest project configuration file from a start path.
    # Inputs/Outputs:
    # Input optional start/home paths; returns .notion_mcp/config.json Path.
    # Usage:
    # ProjectResolver.find_project_config(Path.cwd())
    # --------------------------------
    @staticmethod
    def find_project_config(
        cwd: Path | None = None,
        *,
        home: Path | None = None,
    ) -> Path:
        root = ProjectResolver.find_project_root(cwd, home=home)
        return ProjectPaths(root).config_file

    # --------------------------------
    # Function Description:
    # Finds an existing project or initializes one at a fallback root.
    # Inputs/Outputs:
    # Input cwd/home and init metadata; returns project root and config.
    # Usage:
    # ProjectResolver.ensure_project(Path.cwd())
    # --------------------------------
    @staticmethod
    def ensure_project(
        cwd: Path | None = None,
        *,
        project_name: str | None = None,
        workspace_hint: str | None = None,
        force: bool = False,
        private: bool = False,
        home: Path | None = None,
    ) -> tuple[Path, ProjectConfig]:
        start = Path.cwd() if cwd is None else Path(cwd)
        try:
            root = ProjectResolver.find_project_root(start, home=home)
            return root, ProjectConfigStore.load(root)
        except ProjectConfigNotFoundError:
            root = start.expanduser().resolve()
            config = ProjectConfigStore.init_project(
                root,
                project_name=project_name,
                workspace_hint=workspace_hint,
                force=force,
                private=private,
                home=home,
            )
            return root, config

    # --------------------------------
    # Function Description:
    # Initializes project context in the supplied directory.
    # Inputs/Outputs:
    # Input project root/home and metadata; returns ProjectConfig or rejects the user home.
    # Usage:
    # ProjectResolver.init_project(Path.cwd())
    # --------------------------------
    @staticmethod
    def init_project(
        project_root: Path | None = None,
        *,
        project_name: str | None = None,
        workspace_hint: str | None = None,
        force: bool = False,
        private: bool = False,
        home: Path | None = None,
    ) -> ProjectConfig:
        root = Path.cwd() if project_root is None else Path(project_root)
        return ProjectConfigStore.init_project(
            root,
            project_name=project_name,
            workspace_hint=workspace_hint,
            force=force,
            private=private,
            home=home,
        )
