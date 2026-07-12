# File: src/nilo/cli/commands/data_sources.py
# Format: UTF-8
# =============================
# File Description:
# CLI data source commands backed by Core data source service.
# TAG: cli, data-sources
# =============================

from __future__ import annotations

from pathlib import Path

import typer

from nilo.core.attachments import ContextResolver
from nilo.core.errors import CoreError
from nilo.core.models import dry_run_result
from nilo.core.project import ProjectResolver

from ..aliases import add_group_alias, command_alias
from ..core_services import get_data_sources_service as _get_data_sources_service
from ..core_services import get_pages_service as _get_pages_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="Data source operations")
property_app = typer.Typer(add_completion=False, help="Data source property operations")
page_app = typer.Typer(add_completion=False, help="Data source page operations")


def register(root_app: typer.Typer) -> None:
    app.add_typer(property_app, name="property")
    add_group_alias(app, property_app, "data-source", "property")
    app.add_typer(page_app, name="page")
    add_group_alias(app, page_app, "data-source", "page")
    root_app.add_typer(app, name="data-source")
    add_group_alias(root_app, app, "data-source")
    root_app.add_typer(app, name="data-sources", hidden=True)


def get_data_sources_service():
    return _get_data_sources_service()


def get_pages_service():
    return _get_pages_service()


# --------------------------------
# Function Description:
# Resolves an explicit database id or the current attached database id.
# Inputs/Outputs:
# Input optional database id; returns resolved database id.
# Usage:
# resolve_database_id(None)
# --------------------------------
def resolve_database_id(explicit_database_id: str | None = None) -> str:
    if explicit_database_id:
        return explicit_database_id
    project_root = ProjectResolver.find_project_root(Path.cwd())
    return ContextResolver(project_root).resolve_database_id()


@command_alias(app, "data-source", "retrieve")
@app.command(name="retrieve")
def retrieve(data_source_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    try:
        result = get_data_sources_service().retrieve(data_source_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "data-source", "query")
@app.command(name="query")
def query(
    data_source_id: str,
    payload: str = typer.Option("{}", "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("data_sources.query", {"data_source_id": data_source_id, **data}).__dict__
    else:
        try:
            result = get_data_sources_service().query(data_source_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "data-source", "create")
@app.command(name="create")
def create(
    database_id: str | None = typer.Argument(None),
    payload: str = typer.Option(..., "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        try:
            resolved_database_id = resolve_database_id(database_id)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
        arguments = {"database_id": resolved_database_id, **data}
        result = dry_run_result("data_sources.create", arguments).__dict__
    else:
        try:
            resolved_database_id = resolve_database_id(database_id)
            result = get_data_sources_service().create_for_database(resolved_database_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "data-source", "update")
@app.command(name="update")
def update(
    data_source_id: str,
    payload: str = typer.Option(..., "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("data_sources.update", {"data_source_id": data_source_id, **data}).__dict__
    else:
        try:
            result = get_data_sources_service().update(data_source_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "data-source", "templates")
@app.command(name="templates")
def templates(data_source_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    try:
        result = get_data_sources_service().templates(data_source_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(property_app, "data-source", "property", "rename")
@property_app.command(name="rename")
def property_rename(
    data_source_id: str,
    property_id_or_name: str,
    new_name: str,
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    if dry_run:
        result = dry_run_result(
            "data_sources.property.rename",
            {
                "data_source_id": data_source_id,
                "property_id_or_name": property_id_or_name,
                "new_name": new_name,
            },
        ).__dict__
    else:
        try:
            result = get_data_sources_service().rename_property(data_source_id, property_id_or_name, new_name)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(page_app, "data-source", "page", "create")
@page_app.command(name="create")
def page_create(
    data_source_id: str,
    properties: str = typer.Option(..., "--properties", help="JSON page properties for pages.create"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    payload = {
        "parent": {"type": "data_source_id", "data_source_id": data_source_id},
        "properties": parse_json_object(properties),
    }
    if dry_run:
        result = dry_run_result("pages.create", payload).__dict__
    else:
        try:
            result = get_pages_service().create(payload)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
