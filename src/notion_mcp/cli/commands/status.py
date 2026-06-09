# File: src/notion_mcp/cli/commands/status.py
# Format: UTF-8
# =============================
# File Description:
# CLI status command for local configuration and capability visibility.
# TAG: cli, status
# =============================

from __future__ import annotations

import os

import typer

from notion_mcp.core.config import load_core_config, redacted_config
from notion_mcp.core.errors import ConfigNotFoundError

from ..formatting import echo_json


# --------------------------------
# Function Description:
# Registers the status command.
# Inputs/Outputs:
# Input Typer app; output is app with status command attached.
# Usage:
# register(app)
# --------------------------------
def register(app: typer.Typer) -> None:
    app.command(
        name="status",
        help="Show global configuration and capability status",
        hidden=True,
    )(status_command)


# --------------------------------
# Function Description:
# Builds the local CLI status payload.
# Inputs/Outputs:
# No input; returns a stable status dictionary.
# Usage:
# build_status()
# --------------------------------
def build_status() -> dict[str, object]:
    try:
        config = load_core_config()
        configured = True
        public_config = redacted_config(config)
    except ConfigNotFoundError:
        configured = False
        public_config = {}
    explicit_config_path = bool(os.getenv("NOTION_MCP_CONFIG"))
    return {
        "configured": configured,
        "config": public_config,
        "capabilities": {
            "core": True,
            "mcp_server": not (configured and explicit_config_path),
        },
    }


# --------------------------------
# Function Description:
# Prints local configuration and capability status.
# Inputs/Outputs:
# Optional JSON flag; output is human text or JSON.
# Usage:
# hidden compatibility status --json
# --------------------------------
def status_command(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    status = build_status()
    if json_output:
        echo_json(status)
        return
    configured = "yes" if status["configured"] else "no"
    config = status["config"] if isinstance(status["config"], dict) else {}
    token = "set" if config.get("notion_token_set") else "missing"
    typer.echo(f"Configured: {configured}")
    typer.echo(f"Token: {token}")
    if config.get("user_name"):
        typer.echo(f"User: {config['user_name']}")
    if config.get("notion_version"):
        typer.echo(f"Notion-Version: {config['notion_version']}")
