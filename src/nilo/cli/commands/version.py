# File: src/nilo/cli/commands/version.py
# Format: UTF-8
# =============================
# File Description:
# Root CLI version command for Notion MCP and pinned Notion API version.
# TAG: cli, version
# =============================

from __future__ import annotations

import typer

from nilo import __version__
from nilo.core.config import DEFAULT_NOTION_VERSION, load_core_config
from nilo.core.errors import ConfigNotFoundError

from ..aliases import command_alias
from ..formatting import echo_json


# --------------------------------
# Function Description:
# Registers the root version command.
# Inputs/Outputs:
# Input root Typer app; output is app with version command attached.
# Usage:
# register(app)
# --------------------------------
def register(app: typer.Typer) -> None:
    app.command(
        name="version",
        help="Show Notion MCP and configured Notion API versions",
    )(version_command)
    command_alias(app, "version")(version_command)


# --------------------------------
# Function Description:
# Resolves the configured Notion-Version or the project default.
# Inputs/Outputs:
# No input; returns the configured Notion API version string.
# Usage:
# resolve_notion_version()
# --------------------------------
def resolve_notion_version() -> str:
    try:
        return load_core_config().notion_version
    except ConfigNotFoundError:
        return DEFAULT_NOTION_VERSION


# --------------------------------
# Function Description:
# Prints the Notion MCP package version and Notion-Version.
# Inputs/Outputs:
# Optional JSON flag; output is human text or JSON.
# Usage:
# nilo version --json
# --------------------------------
def version_command(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    payload = {
        "mcp_version": __version__,
        "notion_version": resolve_notion_version(),
    }
    if json_output:
        echo_json(payload)
        return
    typer.echo(f"MCP version: {payload['mcp_version']}")
    typer.echo(f"Notion-Version: {payload['notion_version']}")
