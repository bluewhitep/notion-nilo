# File: src/nilo/cli/commands/search.py
# Format: UTF-8
# =============================
# File Description:
# CLI search commands backed by Core search service.
# TAG: cli, search
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError

from ..aliases import add_group_alias, command_alias
from ..core_services import get_search_service as _get_search_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="Workspace search operations")


def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="search")
    add_group_alias(root_app, app, "search")


def get_search_service():
    return _get_search_service()


@command_alias(app, "search", "query")
@app.command(name="query")
def query(payload: str = typer.Option("{}", "--payload"), json_output: bool = typer.Option(False, "--json")) -> None:
    data = parse_json_object(payload)
    try:
        result = get_search_service().search(data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
