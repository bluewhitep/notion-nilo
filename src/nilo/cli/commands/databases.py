# File: src/nilo/cli/commands/databases.py
# Format: UTF-8
# =============================
# File Description:
# CLI database commands backed by Core database service.
# TAG: cli, databases
# =============================

from __future__ import annotations

from pathlib import Path

import typer

from nilo.core.attachments import (
    ContextResolver,
    DatabaseAttachment,
    DatabaseAttachmentStore,
    PageAttachmentStore,
)
from nilo.core.errors import CoreError
from nilo.core.identifiers import parse_notion_page_id
from nilo.core.models import dry_run_result
from nilo.core.project import ProjectPaths, ProjectResolver

from ..aliases import add_group_alias, command_alias
from ..core_services import get_data_sources_service as _get_data_sources_service
from ..core_services import get_databases_service as _get_databases_service
from ..core_services import get_pages_service as _get_pages_service
from ..core_services import get_raw_api_service as _get_raw_api_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="Database operations")
page_app = typer.Typer(add_completion=False, help="Database page shortcuts")
property_app = typer.Typer(add_completion=False, help="Database property shortcuts")


# --------------------------------
# Function Description:
# Registers database command aliases.
# Inputs/Outputs:
# Input root Typer app; output is app with database/databases subcommands.
# Usage:
# register(root_app)
# --------------------------------
def register(root_app: typer.Typer) -> None:
    app.add_typer(page_app, name="page")
    add_group_alias(app, page_app, "database", "page")
    app.add_typer(property_app, name="property")
    add_group_alias(app, property_app, "database", "property")
    root_app.add_typer(app, name="database")
    add_group_alias(root_app, app, "database")
    root_app.add_typer(app, name="databases", hidden=True)


# --------------------------------
# Function Description:
# Returns the Core databases service.
# Inputs/Outputs:
# No input; returns DatabasesService.
# Usage:
# get_databases_service().retrieve("database-id")
# --------------------------------
def get_databases_service():
    return _get_databases_service()


# --------------------------------
# Function Description:
# Returns the Core data sources service for database shortcuts.
# Inputs/Outputs:
# No input; returns DataSourcesService.
# Usage:
# get_data_sources_service().query("data-source-id", {})
# --------------------------------
def get_data_sources_service():
    return _get_data_sources_service()


# --------------------------------
# Function Description:
# Returns the Core pages service for database page shortcuts.
# Inputs/Outputs:
# No input; returns PagesService.
# Usage:
# get_pages_service().create({"parent": {"data_source_id": "id"}})
# --------------------------------
def get_pages_service():
    return _get_pages_service()


# --------------------------------
# Function Description:
# Returns the Core raw API service for legacy database query compatibility.
# Inputs/Outputs:
# No input; returns RawNotionService.
# Usage:
# get_raw_api_service().invoke("databases.query", {"database_id": "id"})
# --------------------------------
def get_raw_api_service():
    return _get_raw_api_service()


# --------------------------------
# Function Description:
# Builds the JSON payload for database attachment CLI output.
# Inputs/Outputs:
# Input project root and attachment; returns stable dictionary.
# Usage:
# build_database_attachment_status(root, attachment)
# --------------------------------
def build_database_attachment_status(project_root: Path, attachment: DatabaseAttachment) -> dict[str, object]:
    paths = ProjectPaths(project_root)
    return {
        "project_root": str(project_root),
        "state_file": str(paths.database_attachment_file),
        "attachment": attachment.model_dump(mode="json", exclude_none=False),
    }


# --------------------------------
# Function Description:
# Finds the current project and loads the attached database.
# Inputs/Outputs:
# No input; returns project root and DatabaseAttachment.
# Usage:
# load_current_database_attachment()
# --------------------------------
def load_current_database_attachment() -> tuple[Path, DatabaseAttachment]:
    project_root = ProjectResolver.find_project_root(Path.cwd())
    return project_root, DatabaseAttachmentStore.load(project_root)


# --------------------------------
# Function Description:
# Prints attached database status in human-readable form.
# Inputs/Outputs:
# Input project root and attachment; output is terminal text.
# Usage:
# print_database_attachment_status(root, attachment)
# --------------------------------
def print_database_attachment_status(project_root: Path, attachment: DatabaseAttachment) -> None:
    state_file = ProjectPaths(project_root).database_attachment_file
    typer.echo("Attached database")
    typer.echo("Project root:")
    typer.echo(f"  {project_root}")
    typer.echo("State file:")
    typer.echo(f"  {state_file}")
    typer.echo("Database:")
    typer.echo(f"  Title: {attachment.database.title or ''}")
    typer.echo(f"  ID: {attachment.database.id}")
    if attachment.database.url:
        typer.echo(f"  URL: {attachment.database.url}")
    typer.echo(f"  Inline: {attachment.database.is_inline}")
    typer.echo(f"  Archived: {attachment.database.archived}")
    typer.echo(f"  In trash: {attachment.database.in_trash}")
    typer.echo("Active data source:")
    if attachment.active_data_source:
        typer.echo(f"  Name: {attachment.active_data_source.name or ''}")
        typer.echo(f"  ID: {attachment.active_data_source.id}")
    else:
        typer.echo("  None")
    typer.echo("Available data sources:")
    for source in attachment.available_data_sources:
        typer.echo(f"  - {source.name or ''} {source.id}".rstrip())
    typer.echo("Attached at:")
    typer.echo(f"  {attachment.attached_at}")
    typer.echo("Verified at:")
    typer.echo(f"  {attachment.verified_at}")


# --------------------------------
# Function Description:
# Resolves the current attached database id from project context.
# Inputs/Outputs:
# Input optional explicit id; returns database id.
# Usage:
# resolve_database_id("explicit-db")
# --------------------------------
def resolve_database_id(explicit_database_id: str | None = None) -> str:
    if explicit_database_id:
        return explicit_database_id
    project_root = ProjectResolver.find_project_root(Path.cwd())
    return ContextResolver(project_root).resolve_database_id(explicit_database_id)


# --------------------------------
# Function Description:
# Resolves the current active data source id from project context.
# Inputs/Outputs:
# Input optional explicit id; returns data source id.
# Usage:
# resolve_data_source_id("explicit-ds")
# --------------------------------
def resolve_data_source_id(explicit_data_source_id: str | None = None) -> str:
    if explicit_data_source_id:
        return explicit_data_source_id
    project_root = ProjectResolver.find_project_root(Path.cwd())
    return ContextResolver(project_root).resolve_data_source_id(explicit_data_source_id)


# --------------------------------
# Function Description:
# Resolves an explicit parent page or the current attached project page.
# Inputs/Outputs:
# Input optional page id; returns parent page id or raises CoreError.
# Usage:
# resolve_parent_page_id("page-id")
# --------------------------------
def resolve_parent_page_id(explicit_page_id: str | None = None) -> str:
    if explicit_page_id:
        return parse_notion_page_id(explicit_page_id)
    project_root = ProjectResolver.find_project_root(Path.cwd())
    return PageAttachmentStore.load(project_root).page.id


# --------------------------------
# Function Description:
# Adds a page parent to a database create payload when absent.
# Inputs/Outputs:
# Input payload and optional page id; returns payload with parent set.
# Usage:
# with_page_parent({"title": []}, "page-id")
# --------------------------------
def with_page_parent(payload: dict[str, object], parent_page_id: str | None = None) -> dict[str, object]:
    data = dict(payload)
    if "parent" not in data:
        if parent_page_id is not None:
            data["parent"] = {"type": "page_id", "page_id": parse_notion_page_id(parent_page_id)}
        else:
            try:
                data["parent"] = {"type": "page_id", "page_id": resolve_parent_page_id()}
            except CoreError:
                return data
    return data


@command_alias(app, "database", "attach")
@app.command(name="attach")
# --------------------------------
# Function Description:
# Attaches a Notion database as the current project database context.
# Inputs/Outputs:
# Input database id and data source selector; writes database.attach.json and prints status.
# Usage:
# nilo database attach DATABASE_ID --data-source Tasks --json
# --------------------------------
def attach_database(
    database_id: str,
    data_source: str | None = typer.Option(None, "--data-source", help="Active data source id or name"),
    title: str | None = typer.Option(None, "--title", help="Manual title for --no-verify attach"),
    verify: bool = typer.Option(True, "--verify/--no-verify", help="Retrieve the database before writing state"),
    require_project: bool = typer.Option(False, "--require-project", help="Fail if project context is missing"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        if require_project:
            project_root = ProjectResolver.find_project_root(Path.cwd())
        else:
            project_root, _ = ProjectResolver.ensure_project(Path.cwd())
        if verify:
            database_response = get_databases_service().retrieve(database_id)
            attachment = DatabaseAttachment.from_database_response(
                database_response,
                command="nilo database attach",
                data_source_selector=data_source,
            )
        else:
            attachment = DatabaseAttachment.from_manual(
                database_id=database_id,
                title=title,
                command="nilo database attach --no-verify",
            )
        DatabaseAttachmentStore.save(project_root, attachment)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    status = build_database_attachment_status(project_root, attachment)
    if json_output:
        echo_json(status)
    else:
        typer.echo("Attached database:")
        typer.echo(f"  {attachment.database.title or ''}")
        typer.echo(f"  {attachment.database.id}")
        if attachment.active_data_source:
            typer.echo("Active data source:")
            typer.echo(f"  {attachment.active_data_source.name or ''}")
            typer.echo(f"  {attachment.active_data_source.id}")
        typer.echo("State file:")
        typer.echo(f"  {ProjectPaths(project_root).database_attachment_file}")


@command_alias(app, "database", "status")
@app.command(name="status")
@app.command(name="current", hidden=True)
# --------------------------------
# Function Description:
# Shows the current project database attachment.
# Inputs/Outputs:
# Optional JSON/refresh flags; output is human text or JSON.
# Usage:
# nilo database status --json
# --------------------------------
def database_status(
    refresh: bool = typer.Option(False, "--refresh", help="Refresh metadata from Notion before printing"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root, attachment = load_current_database_attachment()
        if refresh:
            database_response = get_databases_service().retrieve(attachment.database.id)
            attachment = attachment.refreshed(database_response, command="nilo database status --refresh")
            DatabaseAttachmentStore.save(project_root, attachment)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(build_database_attachment_status(project_root, attachment))
    else:
        print_database_attachment_status(project_root, attachment)


@command_alias(app, "database", "refresh")
@app.command(name="refresh")
# --------------------------------
# Function Description:
# Refreshes the current database attachment metadata from Notion.
# Inputs/Outputs:
# Optional JSON flag; updates database.attach.json and prints status.
# Usage:
# nilo database refresh --json
# --------------------------------
def database_refresh(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root, attachment = load_current_database_attachment()
        database_response = get_databases_service().retrieve(attachment.database.id)
        updated = attachment.refreshed(database_response, command="nilo database refresh")
        DatabaseAttachmentStore.save(project_root, updated)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(build_database_attachment_status(project_root, updated))
    else:
        print_database_attachment_status(project_root, updated)


@command_alias(app, "database", "detach")
@app.command(name="detach")
@app.command(name="deattach", hidden=True)
# --------------------------------
# Function Description:
# Removes current project database attachment state without touching Notion.
# Inputs/Outputs:
# Optional JSON flag; deletes database.attach.json and prints removed state.
# Usage:
# nilo database detach
# --------------------------------
def database_detach(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root, attachment = load_current_database_attachment()
        state_file = ProjectPaths(project_root).database_attachment_file
        DatabaseAttachmentStore.delete(project_root)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    payload = {
        "project_root": str(project_root),
        "removed": str(state_file),
        "previous_database": attachment.database.model_dump(mode="json", exclude_none=False),
    }
    if json_output:
        echo_json(payload)
    else:
        typer.echo("Detached database:")
        typer.echo(f"  {attachment.database.title or ''}")
        typer.echo(f"  {attachment.database.id}")
        typer.echo("Removed:")
        typer.echo(f"  {state_file}")


@command_alias(app, "database", "retrieve")
@app.command(name="retrieve")
# --------------------------------
# Function Description:
# Retrieves a legacy Notion database through Core.
# Inputs/Outputs:
# Input database_id and JSON flag; output is database response.
# Usage:
# nilo database retrieve DATABASE_ID --json
# --------------------------------
def retrieve(
    database_id: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        resolved_database_id = resolve_database_id(database_id)
        result = get_databases_service().retrieve(resolved_database_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "database", "sources")
@app.command(name="sources")
# --------------------------------
# Function Description:
# Lists data sources under a database container.
# Inputs/Outputs:
# Input database_id; output is child data source list.
# Usage:
# nilo database sources DATABASE_ID --json
# --------------------------------
def sources(
    database_id: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        resolved_database_id = resolve_database_id(database_id)
        data_sources = get_databases_service().list_data_sources(resolved_database_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    result = {"database_id": resolved_database_id, "data_sources": data_sources}
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "database", "create")
@app.command(name="create")
# --------------------------------
# Function Description:
# Creates a Notion database container through Core.
# Inputs/Outputs:
# Input JSON payload; output is create response or dry-run result.
# Usage:
# nilo database create --payload '{"parent": {}}' --json
# --------------------------------
def create(
    payload: str = typer.Option("{}", "--payload", help="JSON payload for databases.create"),
    parent_page: str | None = typer.Option(None, "--parent-page", help="Create under this parent page"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        data = with_page_parent(parse_json_object(payload), parent_page_id=parent_page)
        if dry_run:
            result = dry_run_result("databases.create", data).__dict__
        else:
            result = get_databases_service().create(data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "database", "update")
@app.command(name="update")
# --------------------------------
# Function Description:
# Updates a Notion database container through Core.
# Inputs/Outputs:
# Input database_id and JSON payload; output is update response or dry-run result.
# Usage:
# nilo database update DATABASE_ID --payload '{"title": []}' --json
# --------------------------------
def update(
    database_id: str,
    payload: str = typer.Option(..., "--payload", help="JSON payload for databases.update"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("databases.update", {"database_id": database_id, **data}).__dict__
    else:
        try:
            result = get_databases_service().update(database_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "database", "rename")
@app.command(name="rename")
# --------------------------------
# Function Description:
# Renames a Notion database container through Core.
# Inputs/Outputs:
# Input database_id and new_name; output is update response or dry-run result.
# Usage:
# nilo database rename DATABASE_ID "New Name" --json
# --------------------------------
def rename(
    database_id: str,
    new_name: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    if dry_run:
        result = dry_run_result("databases.rename", {"database_id": database_id, "new_name": new_name}).__dict__
    else:
        try:
            result = get_databases_service().rename(database_id, new_name)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "database", "query", context_settings={"allow_extra_args": True})
@app.command(name="query", context_settings={"allow_extra_args": True})
# --------------------------------
# Function Description:
# Queries a data source or legacy Notion database through Core.
# Inputs/Outputs:
# Input optional compatibility database id and JSON payload; output is query response or dry-run result.
# Usage:
# hidden compatibility database query with explicit database id
# --------------------------------
def query(
    ctx: typer.Context,
    data_source_id: str | None = typer.Option(
        None,
        "--data-source",
        help="Query this data source id explicitly",
        hidden=True,
    ),
    payload: str = typer.Option("{}", "--payload", help="JSON payload for databases.query"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(payload)
    database_id = ctx.args[0] if ctx.args else None
    if data_source_id:
        if dry_run:
            result = dry_run_result("data_sources.query", {"data_source_id": data_source_id, **data}).__dict__
        else:
            try:
                result = get_data_sources_service().query(data_source_id, data)
            except CoreError as exc:
                exit_with_error(exc, json_output=json_output)
    elif database_id:
        if dry_run:
            result = dry_run_result("databases.query", {"database_id": database_id, **data}).__dict__
        else:
            try:
                database_service = get_databases_service()
                legacy_query = getattr(database_service, "query", None)
                if callable(legacy_query):
                    result = legacy_query(database_id, data)
                else:
                    result = get_raw_api_service().invoke("databases.query", {"database_id": database_id, **data})
            except CoreError as exc:
                exit_with_error(exc, json_output=json_output)
    else:
        try:
            resolved_data_source_id = resolve_data_source_id()
            if dry_run:
                result = dry_run_result(
                    "data_sources.query",
                    {"data_source_id": resolved_data_source_id, **data},
                ).__dict__
            else:
                result = get_data_sources_service().query(resolved_data_source_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(page_app, "database", "page", "create", context_settings={"allow_extra_args": True})
@page_app.command(name="create", context_settings={"allow_extra_args": True})
def page_create(
    ctx: typer.Context,
    properties: str = typer.Option(..., "--properties", help="JSON page properties for pages.create"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(properties)
    try:
        compatibility_data_source_id = ctx.args[0] if ctx.args else None
        resolved_data_source_id = resolve_data_source_id(compatibility_data_source_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    payload = {
        "parent": {"type": "data_source_id", "data_source_id": resolved_data_source_id},
        "properties": data,
    }
    if dry_run:
        result = dry_run_result("pages.create", payload).__dict__
    else:
        try:
            result = get_pages_service().create(payload)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@page_app.command(name="update", hidden=True)
def page_update(
    page_id: str,
    properties: str = typer.Option(..., "--properties", help="JSON page properties for pages.update"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    payload = {"properties": parse_json_object(properties)}
    if dry_run:
        result = dry_run_result("pages.update", {"page_id": page_id, **payload}).__dict__
    else:
        try:
            result = get_pages_service().update(page_id, payload)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(property_app, "database", "property", "rename")
@property_app.command(name="rename")
def property_rename(
    property_id_or_name: str,
    new_name: str,
    compatibility_new_name: str | None = typer.Argument(None, hidden=True),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    explicit_data_source_id: str | None = None
    if compatibility_new_name is not None:
        explicit_data_source_id = property_id_or_name
        property_id_or_name = new_name
        new_name = compatibility_new_name
    try:
        resolved_data_source_id = resolve_data_source_id(explicit_data_source_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if dry_run:
        result = dry_run_result(
            "data_sources.property.rename",
            {
                "data_source_id": resolved_data_source_id,
                "property_id_or_name": property_id_or_name,
                "new_name": new_name,
            },
        ).__dict__
    else:
        try:
            result = get_data_sources_service().rename_property(resolved_data_source_id, property_id_or_name, new_name)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)
