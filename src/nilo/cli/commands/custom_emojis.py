# File: src/nilo/cli/commands/custom_emojis.py
# Format: UTF-8
# =============================
# File Description:
# CLI custom emoji commands backed by Core custom emoji service.
# TAG: cli, custom-emojis
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError

from ..aliases import add_group_alias, command_alias
from ..core_services import get_custom_emojis_service as _get_custom_emojis_service
from ..formatting import echo_json, exit_with_error

app = typer.Typer(add_completion=False, help="Custom emoji operations")


def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="custom-emoji")
    add_group_alias(root_app, app, "custom-emoji")
    root_app.add_typer(app, name="custom-emojis", hidden=True)


def get_custom_emojis_service():
    return _get_custom_emojis_service()


@command_alias(app, "custom-emoji", "list")
@app.command(name="list")
def list_emojis(
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
        result = get_custom_emojis_service().list(**params)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "custom-emoji", "retrieve")
@app.command(name="retrieve")
def retrieve(custom_emoji_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    try:
        result = get_custom_emojis_service().retrieve(custom_emoji_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
