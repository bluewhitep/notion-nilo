# File: src/nilo/cli/commands/project.py
# Format: UTF-8
# =============================
# File Description:
# Project-level .notion_mcp context helpers and hidden compatibility aliases.
# TAG: cli, project, local-context
# =============================

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from nilo.core.errors import CoreError
from nilo.core.project import ProjectConfig, ProjectConfigStore, ProjectPaths, ProjectResolver

from ..aliases import command_alias
from ..formatting import echo_json, exit_with_error

app = typer.Typer(add_completion=False, help="Manage project-local Notion context")
local_app = typer.Typer(add_completion=False, help="Compatibility alias for project context commands")


# --------------------------------
# Function Description:
# Registers root project helpers and hidden compatibility command groups.
# Inputs/Outputs:
# Input root Typer app; output is app with command groups attached.
# Usage:
# register(root_app)
# --------------------------------
def register(root_app: typer.Typer) -> None:
    root_app.command(
        name="pwd",
        help="Print resolved Notion project root",
    )(root_command)
    command_alias(root_app, "pwd")(root_command)
    app.command(
        name="init",
        help="Create .notion_mcp project context",
    )(init_command)
    app.command(
        name="status",
        help="Show project-local context status",
    )(status_command)
    app.command(
        name="root",
        help="Print resolved project root",
    )(root_command)
    local_app.command(
        name="init",
        help="Create .notion_mcp project context",
    )(init_command)
    local_app.command(
        name="status",
        help="Show project-local context status",
    )(status_command)
    local_app.command(
        name="root",
        help="Print resolved project root",
    )(root_command)
    root_app.add_typer(app, name="project", hidden=True)
    root_app.add_typer(local_app, name="local", hidden=True)


# --------------------------------
# Function Description:
# Serializes project status for JSON CLI output.
# Inputs/Outputs:
# Input project root and config; returns stable project status dictionary.
# Usage:
# build_project_status(root, config)
# --------------------------------
def build_project_status(project_root: Path, config: ProjectConfig) -> dict[str, Any]:
    paths = ProjectPaths(project_root)
    return {
        "project_root": str(project_root),
        "config_file": str(paths.config_file),
        "state_dir": str(paths.state_dir),
        "cache_dir": str(paths.cache_dir),
        "logs_dir": str(paths.logs_dir),
        "config": config.model_dump(mode="json", exclude_none=True),
        "stores_tokens": False,
    }


# --------------------------------
# Function Description:
# Loads the current project root and config for CLI commands.
# Inputs/Outputs:
# No input; returns project root and ProjectConfig or exits through caller error handling.
# Usage:
# load_current_project()
# --------------------------------
def load_current_project() -> tuple[Path, ProjectConfig]:
    root = ProjectResolver.find_project_root(Path.cwd())
    return root, ProjectConfigStore.load(root)


# --------------------------------
# Function Description:
# Initializes .notion_mcp project context in the current directory.
# Inputs/Outputs:
# CLI options; writes project files and prints human or JSON output.
# Usage:
# nilo init --project-name Demo
# --------------------------------
def init_command(
    project_name: str | None = typer.Option(None, "--project-name", help="Optional project display name"),
    workspace_hint: str | None = typer.Option(None, "--workspace-hint", help="Optional Notion workspace hint"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing project config"),
    private: bool = typer.Option(False, "--private", help="Write project files with 0600 permissions"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    project_root = Path.cwd().resolve()
    try:
        config = ProjectResolver.init_project(
            project_root,
            project_name=project_name,
            workspace_hint=workspace_hint,
            force=force,
            private=private,
        )
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    status = build_project_status(project_root, config)
    if json_output:
        echo_json({"ok": True, **status})
        return
    typer.echo("Created .notion_mcp/.")
    typer.echo("Project root:")
    typer.echo(f"  {project_root}")
    typer.echo("Config file:")
    typer.echo(f"  {ProjectPaths(project_root).config_file}")
    typer.echo("This directory stores project-local Notion context.")
    typer.echo("It does not store Notion tokens.")
    typer.echo("By default, runtime state/cache/logs are ignored by .notion_mcp/.gitignore.")


# --------------------------------
# Function Description:
# Prints current project context status.
# Inputs/Outputs:
# Optional JSON flag; output is human text or JSON.
# Usage:
# nilo config --local --show --json
# --------------------------------
def status_command(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root, config = load_current_project()
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    status = build_project_status(project_root, config)
    if json_output:
        echo_json(status)
        return
    typer.echo("Project context")
    typer.echo("Project root:")
    typer.echo(f"  {status['project_root']}")
    typer.echo("Config file:")
    typer.echo(f"  {status['config_file']}")
    if config.project_name:
        typer.echo("Project name:")
        typer.echo(f"  {config.project_name}")
    if config.workspace_hint:
        typer.echo("Workspace hint:")
        typer.echo(f"  {config.workspace_hint}")
    typer.echo("Does not store Notion tokens: yes")


# --------------------------------
# Function Description:
# Prints the resolved project root.
# Inputs/Outputs:
# Optional JSON flag; output is root path as text or JSON.
# Usage:
# nilo pwd --json
# --------------------------------
def root_command(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root = ProjectResolver.find_project_root(Path.cwd())
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json({"project_root": str(project_root), "config_file": str(ProjectPaths(project_root).config_file)})
    else:
        typer.echo(str(project_root))
