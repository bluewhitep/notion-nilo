# File: src/nilo/cli/commands/views.py
# Format: UTF-8
# =============================
# File Description:
# CLI view commands backed by Core views service.
# TAG: cli, views
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError
from nilo.core.models import dry_run_result

from ..aliases import add_group_alias, command_alias
from ..core_services import get_views_service as _get_views_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="View operations")


def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="view")
    add_group_alias(root_app, app, "view")
    root_app.add_typer(app, name="views", hidden=True)


def get_views_service():
    return _get_views_service()


@command_alias(app, "view", "retrieve")
@app.command(name="retrieve")
def retrieve(view_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    try:
        result = get_views_service().retrieve(view_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "view", "list")
@app.command(name="list")
def list_views(
    payload: str = typer.Option("{}", "--payload"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    try:
        result = get_views_service().list(**data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "view", "query")
@app.command(name="query")
def query(
    view_id: str,
    payload: str = typer.Option("{}", "--payload"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    try:
        result = get_views_service().query(view_id, data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "view", "create")
@app.command(name="create")
def create(
    payload: str = typer.Option(..., "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("views.create", data).__dict__
    else:
        try:
            result = get_views_service().create(data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "view", "update")
@app.command(name="update")
def update(
    view_id: str,
    payload: str = typer.Option(..., "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("views.update", {"view_id": view_id, **data}).__dict__
    else:
        try:
            result = get_views_service().update(view_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
