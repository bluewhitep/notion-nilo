# File: src/nilo/cli/commands/users.py
# Format: UTF-8
# =============================
# File Description:
# CLI user commands backed by Core users service.
# TAG: cli, users
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError

from ..aliases import add_group_alias, command_alias
from ..core_services import get_users_service as _get_users_service
from ..formatting import echo_json, exit_with_error

app = typer.Typer(add_completion=False, help="User operations")


def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="user")
    add_group_alias(root_app, app, "user")
    root_app.add_typer(app, name="users", hidden=True)


def get_users_service():
    return _get_users_service()


@command_alias(app, "user", "me")
@app.command(name="me")
def me(json_output: bool = typer.Option(False, "--json")) -> None:
    try:
        result = get_users_service().me()
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "user", "list")
@app.command(name="list")
def list_users(
    page_size: int | None = typer.Option(None, "--page-size"),
    start_cursor: str | None = typer.Option(None, "--start-cursor"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    params: dict[str, object] = {}
    if page_size is not None:
        params["page_size"] = page_size
    if start_cursor is not None:
        params["start_cursor"] = start_cursor
    try:
        result = get_users_service().list(**params)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "user", "retrieve")
@app.command(name="retrieve")
def retrieve(user_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    try:
        result = get_users_service().retrieve(user_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
