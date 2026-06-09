# File: src/notion_mcp/cli/app.py
# Format: UTF-8
# =============================
# File Description:
# Root Typer CLI application for human-facing Notion MCP commands.
# TAG: cli, app
# =============================

from __future__ import annotations

import typer

from .commands import (
    auth,
    blocks,
    comments,
    config,
    custom_emojis,
    data_sources,
    databases,
    file_uploads,
    init,
    pages,
    project,
    raw_api,
    search,
    server,
    status,
    users,
    version,
    views,
)

app = typer.Typer(
    add_completion=False,
    help=(
        "Local Notion MCP CLI. Show global configuration and capability "
        "status with config --global --show."
    ),
)


# --------------------------------
# Function Description:
# Registers all CLI command groups on the root Typer app.
# Inputs/Outputs:
# No input; output is mutation of the root app command registry.
# Usage:
# register_commands()
# --------------------------------
def register_commands() -> None:
    init.register(app)
    status.register(app)
    project.register(app)
    version.register(app)
    config.register(app)
    auth.register(app)
    pages.register(app)
    blocks.register(app)
    databases.register(app)
    data_sources.register(app)
    users.register(app)
    comments.register(app)
    views.register(app)
    file_uploads.register(app)
    search.register(app)
    custom_emojis.register(app)
    raw_api.register(app)
    server.register(app)


register_commands()
