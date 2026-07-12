# File: src/nilo/cli/commands/config.py
# Format: UTF-8
# =============================
# File Description:
# Git-like CLI configuration commands backed by Core config.
# TAG: cli, config
# =============================

from __future__ import annotations

from typing import Any

import typer

from nilo.core.config import (
    CoreConfig,
    load_global_core_config,
    redacted_config,
    save_core_config,
)
from nilo.core.errors import ConfigNotFoundError, ConfigValidationError

from ..aliases import add_group_alias
from ..formatting import echo_json, exit_with_error
from . import project as project_commands

app = typer.Typer(
    add_completion=False,
    invoke_without_command=True,
    context_settings={"allow_extra_args": True},
    help=(
        "Read and update configuration. Examples: config --global --show; "
        "config --global user.token VALUE; config --global user.name NAME; "
        "config --local --show."
    ),
)
global_app = typer.Typer(add_completion=False, help="Read and update global configuration")
local_app = typer.Typer(add_completion=False, help="Read project-local configuration")
CONFIG_FIELDS = set(CoreConfig.model_fields)
PUBLIC_GLOBAL_KEYS = {
    "user.token": "notion_token",
    "user.name": "user_name",
}


# --------------------------------
# Function Description:
# Registers the config sub-application.
# Inputs/Outputs:
# Input root Typer app; output is app with config commands attached.
# Usage:
# register(root_app)
# --------------------------------
def register(root_app: typer.Typer) -> None:
    app.command(
        name="user.token",
        help="Set the global Notion token",
        hidden=True,
    )(set_user_token_key)
    app.command(
        name="user.name",
        help="Set the global user display name",
        hidden=True,
    )(set_user_name_key)
    global_app.command(
        name="set",
        help="Set a global configuration value",
    )(set_value)
    global_app.command(
        name="get",
        help="Get a global configuration value",
    )(get_value)
    global_app.command(
        name="unset",
        help="Unset a nullable global configuration value",
    )(unset_value)
    global_app.command(
        name="list",
        help="List global configuration values",
    )(list_values)
    local_app.command(
        name="init",
        help="Create .notion_mcp project context",
    )(project_commands.init_command)
    local_app.command(
        name="status",
        help="Show project-local context status",
    )(project_commands.status_command)
    local_app.command(
        name="root",
        help="Print resolved project root",
    )(project_commands.root_command)
    app.add_typer(global_app, name="global", hidden=True)
    app.add_typer(local_app, name="local", hidden=True)
    root_app.add_typer(app, name="config")
    add_group_alias(root_app, app, "config")


@app.callback(invoke_without_command=True)
# --------------------------------
# Function Description:
# Handles the public flag-based configuration workflow.
# Inputs/Outputs:
# Input --global/--local flags and optional key/value; output is status or update text.
# Usage:
# nilo config --global user.token "secret"
# --------------------------------
def config_callback(
    ctx: typer.Context,
    global_config: bool = typer.Option(False, "--global", help="Use global user configuration"),
    local_config: bool = typer.Option(False, "--local", help="Use project-local configuration"),
    show: bool = typer.Option(False, "--show", help="Show the selected configuration"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    ctx.obj = {"global": global_config, "local": local_config}
    if ctx.invoked_subcommand is not None:
        return
    if global_config == local_config:
        exit_with_error(
            ConfigValidationError("Pass exactly one of --global or --local"),
            json_output=json_output,
        )
    if global_config:
        if show:
            show_global_config(json_output=json_output)
            return
        exit_with_error(
            ConfigValidationError("Use --show or pass a supported global key and value"),
            json_output=json_output,
        )
    if show:
        project_commands.status_command(json_output=json_output)
        return
    exit_with_error(
        ConfigValidationError("Local configuration updates are handled by project commands"),
        json_output=json_output,
    )


# --------------------------------
# Function Description:
# Converts public flag-based config keys to CoreConfig fields.
# Inputs/Outputs:
# Input public key; returns CoreConfig field or exits with a validation error.
# Usage:
# public_global_key_to_field("user.token")
# --------------------------------
def public_global_key_to_field(key: str) -> str:
    mapped = PUBLIC_GLOBAL_KEYS.get(key)
    if mapped is None:
        raise ConfigValidationError(
            "Unsupported global configuration key",
            details={"key": key, "supported_keys": sorted(PUBLIC_GLOBAL_KEYS)},
        )
    return mapped


# --------------------------------
# Function Description:
# Builds a compact global configuration status payload.
# Inputs/Outputs:
# No input; returns token-safe global configuration status.
# Usage:
# build_global_config_status()
# --------------------------------
def build_global_config_status() -> dict[str, object]:
    try:
        config = load_global_core_config()
        configured = True
    except ConfigNotFoundError:
        config = CoreConfig()
        configured = False
    return {
        "configured": configured,
        "token_set": bool(config.notion_token),
        "user": {
            "name": config.user_name,
            "id": config.user_id,
        },
        "notion_version": config.notion_version,
    }


# --------------------------------
# Function Description:
# Prints global configuration status without exposing token secrets.
# Inputs/Outputs:
# Optional JSON flag; output is human text or JSON.
# Usage:
# nilo config --global --show --json
# --------------------------------
def show_global_config(json_output: bool = False) -> None:
    payload = build_global_config_status()
    if json_output:
        echo_json(payload)
        return
    configured = "yes" if payload["configured"] else "no"
    token = "set" if payload["token_set"] else "missing"
    user = payload["user"] if isinstance(payload["user"], dict) else {}
    user_name = user.get("name") or "not set"
    typer.echo(f"Configured: {configured}")
    typer.echo(f"Token: {token}")
    typer.echo(f"User: {user_name}")
    if user.get("id"):
        typer.echo(f"User ID: {user['id']}")
    typer.echo(f"Notion-Version: {payload['notion_version']}")


# --------------------------------
# Function Description:
# Updates one public global configuration value.
# Inputs/Outputs:
# Input public key/value; writes global config and prints update confirmation.
# Usage:
# set_public_global_value("user.name", "Ada")
# --------------------------------
def set_public_global_value(key: str, value: str, json_output: bool = False) -> None:
    try:
        field = public_global_key_to_field(key)
        try:
            config = load_global_core_config()
        except ConfigNotFoundError:
            config = CoreConfig()
        current = config.model_dump()
        current[field] = value
        updated = CoreConfig(**current)
        save_core_config(updated)
    except ConfigValidationError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json({"ok": True, "key": key})
        return
    typer.echo(f"{key} updated")


# --------------------------------
# Function Description:
# Ensures flag-based public key commands are used with --global.
# Inputs/Outputs:
# Input Typer context; returns None or exits with error.
# Usage:
# require_global_context(ctx)
# --------------------------------
def require_global_context(ctx: typer.Context, json_output: bool = False) -> None:
    parent_obj = ctx.parent.obj if ctx.parent is not None and isinstance(ctx.parent.obj, dict) else {}
    if parent_obj.get("global") is True and parent_obj.get("local") is False:
        return
    exit_with_error(
        ConfigValidationError("Use --global when setting user configuration"),
        json_output=json_output,
    )


# --------------------------------
# Function Description:
# Hidden command backing `config --global user.token VALUE`.
# Inputs/Outputs:
# Input token; writes global config.
# Usage:
# nilo config --global user.token secret
# --------------------------------
def set_user_token_key(
    ctx: typer.Context,
    value: str,
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    require_global_context(ctx, json_output=json_output)
    set_public_global_value("user.token", value, json_output=json_output)


# --------------------------------
# Function Description:
# Hidden command backing `config --global user.name VALUE`.
# Inputs/Outputs:
# Input user name; writes global config.
# Usage:
# nilo config --global user.name Ada
# --------------------------------
def set_user_name_key(
    ctx: typer.Context,
    value: str,
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    require_global_context(ctx, json_output=json_output)
    set_public_global_value("user.name", value, json_output=json_output)


# --------------------------------
# Function Description:
# Validates a CoreConfig field name.
# Inputs/Outputs:
# Input key string; returns key or raises typer.BadParameter.
# Usage:
# require_known_key("user_name")
# --------------------------------
def require_known_key(key: str) -> str:
    if key not in CONFIG_FIELDS:
        typer.echo(f"unknown config key: {key}")
        raise typer.Exit(code=1)
    return key


# --------------------------------
# Function Description:
# Casts string CLI values to the target CoreConfig field type.
# Inputs/Outputs:
# Input key/value strings; returns typed value.
# Usage:
# cast_value("retry", "false")
# --------------------------------
def cast_value(key: str, value: str) -> Any:
    if key in {"retry", "audit_enabled"}:
        return value.lower() in {"1", "true", "yes", "on"}
    if key == "timeout_ms":
        return int(value)
    return value


@app.command(name="set", hidden=True)
# --------------------------------
# Function Description:
# Sets a Core configuration key.
# Inputs/Outputs:
# Input key and value; output is human text or JSON.
# Usage:
# nilo config set user_name Ada
# --------------------------------
def set_value(
    key: str,
    value: str,
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    require_known_key(key)
    try:
        config = load_global_core_config()
    except ConfigNotFoundError:
        config = CoreConfig()
    current = config.model_dump()
    current[key] = cast_value(key, value)
    try:
        updated = CoreConfig(**current)
        save_core_config(updated)
    except ConfigValidationError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json({"ok": True, "key": key})
    else:
        typer.echo(f"{key} updated")


@app.command(name="get", hidden=True)
# --------------------------------
# Function Description:
# Gets a Core configuration key with token redaction by default.
# Inputs/Outputs:
# Input key; output is human text or JSON.
# Usage:
# nilo config get user_name --json
# --------------------------------
def get_value(
    key: str,
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
    show_secret: bool = typer.Option(False, "--show-secret", help="Print secret values"),
) -> None:
    require_known_key(key)
    try:
        config = load_global_core_config()
    except ConfigNotFoundError as exc:
        exit_with_error(exc, json_output=json_output)
    if key == "notion_token" and not show_secret:
        value: Any = "********" if config.notion_token else None
    else:
        value = getattr(config, key)
    if json_output:
        echo_json({"key": key, "value": value})
    else:
        typer.echo(f"{key}={value}")


@app.command(name="unset", hidden=True)
# --------------------------------
# Function Description:
# Clears a nullable Core configuration key.
# Inputs/Outputs:
# Input key; output is human text or JSON.
# Usage:
# nilo config unset user_name
# --------------------------------
def unset_value(
    key: str,
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    require_known_key(key)
    if key in {"notion_version", "timeout_ms", "retry", "default_transport", "audit_enabled"}:
        raise typer.BadParameter(f"{key} cannot be unset")
    try:
        config = load_global_core_config()
    except ConfigNotFoundError as exc:
        exit_with_error(exc, json_output=json_output)
    current = config.model_dump()
    current[key] = None
    updated = CoreConfig(**current)
    save_core_config(updated)
    if json_output:
        echo_json({"ok": True, "key": key})
    else:
        typer.echo(f"{key} cleared")


@app.command(name="list", hidden=True)
# --------------------------------
# Function Description:
# Lists local Core configuration with secret redaction.
# Inputs/Outputs:
# Optional JSON flag; output is human text or JSON.
# Usage:
# nilo config list --json
# --------------------------------
def list_values(json_output: bool = typer.Option(False, "--json", help="Print JSON output")) -> None:
    try:
        config = load_global_core_config()
    except ConfigNotFoundError as exc:
        exit_with_error(exc, json_output=json_output)
    public = redacted_config(config)
    if json_output:
        echo_json(public)
    else:
        for key, value in public.items():
            typer.echo(f"{key}={value}")
