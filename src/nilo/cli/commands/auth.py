# File: src/nilo/cli/commands/auth.py
# Format: UTF-8
# =============================
# File Description:
# CLI auth commands backed by Core auth service.
# TAG: cli, auth
# =============================

from __future__ import annotations

import typer

from nilo.core.auth import AuthService
from nilo.core.client import create_notion_client
from nilo.core.config import load_core_config
from nilo.core.errors import CoreError

from ..aliases import add_group_alias, command_alias
from ..formatting import echo_json, exit_with_error

app = typer.Typer(add_completion=False, help="Validate Notion authentication")


# --------------------------------
# Function Description:
# Registers auth subcommands.
# Inputs/Outputs:
# Input root Typer app; output is app with auth subcommands.
# Usage:
# register(root_app)
# --------------------------------
def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="auth")
    add_group_alias(root_app, app, "auth")


@command_alias(app, "auth", "validate")
@app.command(name="validate")
# --------------------------------
# Function Description:
# Validates the configured Notion token.
# Inputs/Outputs:
# Optional JSON flag; output is validation result.
# Usage:
# nilo auth validate --json
# --------------------------------
def validate(json_output: bool = typer.Option(False, "--json", help="Print JSON output")) -> None:
    try:
        config = load_core_config()
        result = AuthService(create_notion_client(config)).validate(expected_user_id=config.user_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    payload = {
        "valid": result.valid,
        "user_id": result.user_id,
        "name": result.name,
    }
    if json_output:
        echo_json(payload)
    else:
        typer.echo(f"Valid: {'yes' if result.valid else 'no'}")


@command_alias(app, "auth", "whoami")
@app.command(name="whoami")
# --------------------------------
# Function Description:
# Prints the current Notion user associated with the configured token.
# Inputs/Outputs:
# Optional JSON flag; output is user identity.
# Usage:
# nilo auth whoami --json
# --------------------------------
def whoami(json_output: bool = typer.Option(False, "--json", help="Print JSON output")) -> None:
    validate(json_output=json_output)
