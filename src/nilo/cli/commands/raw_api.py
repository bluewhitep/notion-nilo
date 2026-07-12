# File: src/nilo/cli/commands/raw_api.py
# Format: UTF-8
# =============================
# File Description:
# CLI raw API commands backed by Core registered raw API service.
# TAG: cli, raw-api
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError
from nilo.core.services.raw_api import registered_operations

from ..aliases import add_group_alias, command_alias
from ..core_services import get_raw_api_service as _get_raw_api_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="Advanced fallback for registered raw API operations")


def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="raw-api")
    add_group_alias(root_app, app, "raw-api")


def get_raw_api_service():
    return _get_raw_api_service()


@command_alias(app, "raw-api", "operations")
@app.command(name="operations")
def operations(json_output: bool = typer.Option(False, "--json")) -> None:
    result = {"operations": list(registered_operations())}
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "raw-api", "invoke")
@app.command(name="invoke")
def invoke(
    operation: str,
    arguments: str = typer.Option("{}", "--arguments"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(arguments)
    try:
        result = get_raw_api_service().invoke(operation, data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
