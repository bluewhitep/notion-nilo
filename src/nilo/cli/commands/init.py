# File: src/nilo/cli/commands/init.py
# Format: UTF-8
# =============================
# File Description:
# Root project initialization alias for .notion_mcp local context.
# TAG: cli, init, project, local-context
# =============================

from __future__ import annotations

import typer

from ..aliases import command_alias
from . import project


# --------------------------------
# Function Description:
# Registers root init as a project-level initialization alias.
# Inputs/Outputs:
# Input Typer app; output is app with root init command attached.
# Usage:
# register(app)
# --------------------------------
def register(app: typer.Typer) -> None:
    app.command(
        name="init",
        help="Initialize project-local .notion_mcp context",
    )(project.init_command)
    command_alias(app, "init")(project.init_command)
