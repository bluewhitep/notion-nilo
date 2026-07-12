# File: src/nilo/cli/commands/pages.py
# Format: UTF-8
# =============================
# File Description:
# CLI page commands backed by Core page service.
# TAG: cli, pages
# =============================

from __future__ import annotations

from pathlib import Path
from typing import cast

import typer

from nilo.core.attachments import PageAttachment, PageAttachmentStore
from nilo.core.errors import CoreError
from nilo.core.identifiers import parse_notion_page_id
from nilo.core.models import dry_run_result
from nilo.core.project import ProjectPaths, ProjectResolver

from ..aliases import add_group_alias, command_alias
from ..core_services import (
    get_blocks_service as _get_blocks_service,
    get_databases_service as _get_databases_service,
    get_pages_service as _get_pages_service,
)
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="Page operations")
page_block_app = typer.Typer(add_completion=False, help="Page-scoped block operations")
page_insert_app = typer.Typer(add_completion=False, help="Insert objects under the current page")


# --------------------------------
# Function Description:
# Registers page command aliases.
# Inputs/Outputs:
# Input root Typer app; output is app with page/pages subcommands.
# Usage:
# register(root_app)
# --------------------------------
def register(root_app: typer.Typer) -> None:
    app.add_typer(page_block_app, name="block", hidden=True)
    app.add_typer(page_insert_app, name="insert", hidden=True)
    root_app.add_typer(app, name="page")
    add_group_alias(root_app, app, "page")
    root_app.add_typer(app, name="pages", hidden=True)


# --------------------------------
# Function Description:
# Returns the Core pages service.
# Inputs/Outputs:
# No input; returns PagesService.
# Usage:
# get_pages_service().retrieve("page-id")
# --------------------------------
def get_pages_service():
    return _get_pages_service()


# --------------------------------
# Function Description:
# Returns the Core blocks service for page-scoped block commands.
# Inputs/Outputs:
# No input; returns BlocksService.
# Usage:
# get_blocks_service().append_children("block-id", children=[])
# --------------------------------
def get_blocks_service():
    return _get_blocks_service()


# --------------------------------
# Function Description:
# Returns the Core databases service for page insert database commands.
# Inputs/Outputs:
# No input; returns DatabasesService.
# Usage:
# get_databases_service().create(payload)
# --------------------------------
def get_databases_service():
    return _get_databases_service()


# --------------------------------
# Function Description:
# Builds the JSON payload for page attachment CLI output.
# Inputs/Outputs:
# Input project root and attachment; returns stable dictionary.
# Usage:
# build_page_attachment_status(root, attachment)
# --------------------------------
def build_page_attachment_status(project_root: Path, attachment: PageAttachment) -> dict[str, object]:
    paths = ProjectPaths(project_root)
    return {
        "project_root": str(project_root),
        "state_file": str(paths.page_attachment_file),
        "attachment": attachment.model_dump(mode="json", exclude_none=False),
    }


# --------------------------------
# Function Description:
# Finds the current project and loads the attached page.
# Inputs/Outputs:
# No input; returns project root and PageAttachment.
# Usage:
# load_current_page_attachment()
# --------------------------------
def load_current_page_attachment() -> tuple[Path, PageAttachment]:
    project_root = ProjectResolver.find_project_root(Path.cwd())
    return project_root, PageAttachmentStore.load(project_root)


# --------------------------------
# Function Description:
# Prints attached page status in human-readable form.
# Inputs/Outputs:
# Input project root and attachment; output is terminal text.
# Usage:
# print_page_attachment_status(root, attachment)
# --------------------------------
def print_page_attachment_status(project_root: Path, attachment: PageAttachment) -> None:
    state_file = ProjectPaths(project_root).page_attachment_file
    typer.echo("Attached page")
    typer.echo("Project root:")
    typer.echo(f"  {project_root}")
    typer.echo("State file:")
    typer.echo(f"  {state_file}")
    typer.echo("Page:")
    typer.echo(f"  Title: {attachment.page.title or ''}")
    typer.echo(f"  ID: {attachment.page.id}")
    if attachment.page.url:
        typer.echo(f"  URL: {attachment.page.url}")
    typer.echo(f"  Archived: {attachment.page.archived}")
    typer.echo(f"  In trash: {attachment.page.in_trash}")
    typer.echo("Attached at:")
    typer.echo(f"  {attachment.attached_at}")
    typer.echo("Verified at:")
    typer.echo(f"  {attachment.verified_at}")


# --------------------------------
# Function Description:
# Resolves the current attached page id from project context.
# Inputs/Outputs:
# No input; returns attached page id or raises CoreError.
# Usage:
# resolve_attached_page_id()
# --------------------------------
def resolve_attached_page_id() -> str:
    project_root = ProjectResolver.find_project_root(Path.cwd())
    return PageAttachmentStore.load(project_root).page.id


# --------------------------------
# Function Description:
# Adds the attached page parent to a payload when no explicit parent is set.
# Inputs/Outputs:
# Input payload dictionary; returns a copy with parent set.
# Usage:
# with_attached_page_parent({"properties": {}})
# --------------------------------
def with_attached_page_parent(
    payload: dict[str, object],
    parent_page_id: str | None = None,
) -> dict[str, object]:
    data = dict(payload)
    if "parent" not in data:
        resolved_parent_id = parse_notion_page_id(parent_page_id) if parent_page_id else resolve_attached_page_id()
        data["parent"] = {"type": "page_id", "page_id": resolved_parent_id}
    return data


# --------------------------------
# Function Description:
# Prints a stable human-readable page content summary.
# Inputs/Outputs:
# Input content dictionary from Core; output is terminal text.
# Usage:
# print_page_content(result)
# --------------------------------
def print_page_content(result: dict[str, object]) -> None:
    raw_page = result.get("page")
    page = cast(dict[str, object], raw_page) if isinstance(raw_page, dict) else {}
    raw_blocks = result.get("blocks")
    blocks = cast(list[object], raw_blocks) if isinstance(raw_blocks, list) else []
    page_title = page.get("title") or page.get("id") or ""
    typer.echo(f"Page: {page_title}")
    typer.echo(f"ID: {page.get('id', '')}")
    typer.echo("Properties:")
    properties = page.get("properties")
    if isinstance(properties, dict) and properties:
        for key, value in properties.items():
            if isinstance(value, dict) and isinstance(value.get("type"), str):
                typer.echo(f"- {key}: {value['type']}")
            else:
                typer.echo(f"- {key}: {value}")
    typer.echo("Blocks:")
    for index, block in enumerate(blocks, start=1):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type", "")
        block_id = block.get("id", "")
        text = block.get("text", "")
        typer.echo(f'{index}. [{block_type}] block_id={block_id} "{text}"')


@command_alias(app, "page", "attach")
@app.command(name="attach")
# --------------------------------
# Function Description:
# Attaches a Notion page as the current project page context.
# Inputs/Outputs:
# Input page id and verify options; writes page.attach.json and prints status.
# Usage:
# nilo page attach PAGE_ID --json
# --------------------------------
def attach_page(
    page_id: str,
    title: str | None = typer.Option(None, "--title", help="Manual title for --no-verify attach"),
    verify: bool = typer.Option(True, "--verify/--no-verify", help="Retrieve the page before writing state"),
    require_project: bool = typer.Option(False, "--require-project", help="Fail if project context is missing"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        resolved_page_id = parse_notion_page_id(page_id)
        if require_project:
            project_root = ProjectResolver.find_project_root(Path.cwd())
        else:
            project_root, _ = ProjectResolver.ensure_project(Path.cwd())
        if verify:
            page_response = get_pages_service().retrieve(resolved_page_id)
            attachment = PageAttachment.from_page_response(page_response, command="nilo page attach")
        else:
            attachment = PageAttachment.from_manual(
                page_id=resolved_page_id,
                title=title,
                command="nilo page attach --no-verify",
            )
        PageAttachmentStore.save(project_root, attachment)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    status = build_page_attachment_status(project_root, attachment)
    if json_output:
        echo_json(status)
    else:
        typer.echo("Attached page:")
        typer.echo(f"  {attachment.page.title or ''}")
        typer.echo(f"  {attachment.page.id}")
        typer.echo("State file:")
        typer.echo(f"  {ProjectPaths(project_root).page_attachment_file}")


@command_alias(app, "page", "status")
@app.command(name="status")
@app.command(name="current", hidden=True)
# --------------------------------
# Function Description:
# Shows the current project page attachment.
# Inputs/Outputs:
# Optional JSON flag; output is human text or JSON.
# Usage:
# nilo page status --json
# --------------------------------
def page_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root, attachment = load_current_page_attachment()
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(build_page_attachment_status(project_root, attachment))
    else:
        print_page_attachment_status(project_root, attachment)


@command_alias(app, "page", "refresh")
@app.command(name="refresh")
# --------------------------------
# Function Description:
# Refreshes the current page attachment metadata from Notion.
# Inputs/Outputs:
# Optional JSON flag; updates page.attach.json and prints status.
# Usage:
# nilo page refresh --json
# --------------------------------
def page_refresh(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root, attachment = load_current_page_attachment()
        page_response = get_pages_service().retrieve(attachment.page.id)
        updated = attachment.refreshed(page_response, command="nilo page refresh")
        PageAttachmentStore.save(project_root, updated)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(build_page_attachment_status(project_root, updated))
    else:
        print_page_attachment_status(project_root, updated)


@command_alias(app, "page", "detach")
@app.command(name="detach")
@app.command(name="deattach", hidden=True)
# --------------------------------
# Function Description:
# Removes the current project page attachment state without touching Notion.
# Inputs/Outputs:
# Optional JSON flag; deletes page.attach.json and prints removed state.
# Usage:
# nilo page detach
# --------------------------------
def page_detach(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        project_root, attachment = load_current_page_attachment()
        state_file = ProjectPaths(project_root).page_attachment_file
        PageAttachmentStore.delete(project_root)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    payload = {
        "project_root": str(project_root),
        "removed": str(state_file),
        "previous_page": attachment.page.model_dump(mode="json", exclude_none=False),
    }
    if json_output:
        echo_json(payload)
    else:
        typer.echo("Detached page:")
        typer.echo(f"  {attachment.page.title or ''}")
        typer.echo(f"  {attachment.page.id}")
        typer.echo("Removed:")
        typer.echo(f"  {state_file}")


@app.command(name="content", hidden=True)
# --------------------------------
# Function Description:
# Reads page properties and child block summaries.
# Inputs/Outputs:
# Optional page id and flags; output is human text or JSON content.
# Usage:
# hidden compatibility page content --json
# --------------------------------
def page_content(
    page_id: str | None = typer.Argument(None),
    tree: bool = typer.Option(False, "--tree", help="Recursively include child blocks"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        resolved_page_id = parse_notion_page_id(page_id) if page_id else resolve_attached_page_id()
        result = get_pages_service().content(resolved_page_id, tree=tree)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        print_page_content(result)


@command_alias(app, "page", "blocks")
@app.command(name="blocks")
# --------------------------------
# Function Description:
# Reads page child block summaries from an explicit or attached page.
# Inputs/Outputs:
# Optional page id and tree flag; output is block summary content.
# Usage:
# nilo page blocks --json
# --------------------------------
def page_blocks(
    page_id: str | None = typer.Argument(None),
    tree: bool = typer.Option(False, "--tree", help="Recursively include child blocks"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        resolved_page_id = parse_notion_page_id(page_id) if page_id else resolve_attached_page_id()
        result = get_pages_service().content(resolved_page_id, tree=tree)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        print_page_content(result)


@page_block_app.command(name="append")
# --------------------------------
# Function Description:
# Appends child blocks under a block inside the page workflow.
# Inputs/Outputs:
# Input block id and JSON payload; output append result or dry-run payload.
# Usage:
# hidden compatibility page block append
# --------------------------------
def page_block_append(
    block_id: str,
    payload: str = typer.Option(..., "--payload", help="JSON payload with children/position"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(payload)
    children = _children_from_payload(data)
    position = data.get("position")
    if dry_run:
        result = dry_run_result("blocks.children.append", {"block_id": block_id, **data}).__dict__
    else:
        try:
            result = get_blocks_service().append_children(
                block_id,
                children=children,
                position=position if isinstance(position, dict) else None,
            )
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@page_block_app.command(name="insert-after")
# --------------------------------
# Function Description:
# Inserts block children after an existing sibling block.
# Inputs/Outputs:
# Input target block id and payload; output append result or dry-run payload.
# Usage:
# hidden compatibility page block insert-after
# --------------------------------
def page_block_insert_after(
    block_id: str,
    payload: str = typer.Option(..., "--payload", help="JSON payload with children"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(payload)
    children = _children_from_payload(data)
    position = {"type": "after_block", "after_block": {"id": block_id}}
    if dry_run:
        result = dry_run_result("blocks.children.append", {"after": block_id, "position": position, **data}).__dict__
    else:
        try:
            target = get_blocks_service().retrieve(block_id)
            parent_id = _parent_id_for_append(target)
            result = get_blocks_service().append_children(parent_id, children=children, position=position)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@page_block_app.command(name="update")
# --------------------------------
# Function Description:
# Updates a block inside the page workflow.
# Inputs/Outputs:
# Input block id and payload; output update result or dry-run payload.
# Usage:
# hidden compatibility page block update
# --------------------------------
def page_block_update(
    block_id: str,
    payload: str = typer.Option(..., "--payload", help="JSON payload for blocks.update"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("blocks.update", {"block_id": block_id, **data}).__dict__
    else:
        try:
            result = get_blocks_service().update(block_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@page_block_app.command(name="remove")
# --------------------------------
# Function Description:
# Moves a block to trash inside the page workflow.
# Inputs/Outputs:
# Input block id; output trash result or dry-run payload.
# Usage:
# hidden compatibility page block remove
# --------------------------------
def page_block_remove(
    block_id: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    if dry_run:
        result = dry_run_result("blocks.delete", {"block_id": block_id}).__dict__
    else:
        try:
            result = get_blocks_service().trash(block_id)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@page_insert_app.command(name="page")
# --------------------------------
# Function Description:
# Creates a child page under the attached page unless payload supplies a parent.
# Inputs/Outputs:
# Input create-page payload; output create result or dry-run payload.
# Usage:
# hidden compatibility page insert page
# --------------------------------
def page_insert_page(
    payload: str = typer.Option(..., "--payload", help="JSON payload for pages.create"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        data = with_attached_page_parent(parse_json_object(payload))
        if dry_run:
            result = dry_run_result("pages.create", data).__dict__
        else:
            result = get_pages_service().create(data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@page_insert_app.command(name="database")
# --------------------------------
# Function Description:
# Creates a child database under the attached page unless payload supplies a parent.
# Inputs/Outputs:
# Input create-database payload; output create result or dry-run payload.
# Usage:
# hidden compatibility page insert database
# --------------------------------
def page_insert_database(
    payload: str = typer.Option(..., "--payload", help="JSON payload for databases.create"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        data = with_attached_page_parent(parse_json_object(payload))
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


# --------------------------------
# Function Description:
# Extracts children list from a block append payload.
# Inputs/Outputs:
# Input parsed payload; returns child block list.
# Usage:
# _children_from_payload({"children": []})
# --------------------------------
def _children_from_payload(data: dict[str, object]) -> list[dict[str, object]]:
    children = data.get("children", [])
    if not isinstance(children, list):
        return []
    return [child for child in children if isinstance(child, dict)]


# --------------------------------
# Function Description:
# Finds the parent id to pass as block_id for append-after operations.
# Inputs/Outputs:
# Input target block response; returns parent page/block/data source id.
# Usage:
# _parent_id_for_append(block)
# --------------------------------
def _parent_id_for_append(block: dict[str, object]) -> str:
    parent = block.get("parent")
    if isinstance(parent, dict):
        parent_type = parent.get("type")
        if isinstance(parent_type, str):
            typed_value = parent.get(parent_type)
            if isinstance(typed_value, str):
                return typed_value
        for key in ("page_id", "block_id", "data_source_id", "database_id"):
            value = parent.get(key)
            if isinstance(value, str):
                return value
    raise CoreError("Cannot determine parent for target block", details={"block": block})


@command_alias(app, "page", "retrieve")
@app.command(name="retrieve")
# --------------------------------
# Function Description:
# Retrieves a Notion page through Core.
# Inputs/Outputs:
# Input page_id and JSON flag; output is page response.
# Usage:
# nilo page retrieve PAGE_ID --json
# --------------------------------
def retrieve_page(
    page_id: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        resolved_page_id = parse_notion_page_id(page_id) if page_id else resolve_attached_page_id()
        result = get_pages_service().retrieve(resolved_page_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "page", "create")
@app.command(name="create")
# --------------------------------
# Function Description:
# Creates a Notion page through Core or prints dry-run payload.
# Inputs/Outputs:
# Input JSON payload and dry-run flag; output is create response or dry-run result.
# Usage:
# nilo page create --payload '{"parent": {}}' --dry-run --json
# --------------------------------
def create_page(
    payload: str = typer.Option("{}", "--payload", help="JSON payload for pages.create"),
    parent_page: str | None = typer.Option(None, "--parent-page", help="Create under this parent page"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        data = with_attached_page_parent(parse_json_object(payload), parent_page_id=parent_page)
        if dry_run:
            result = dry_run_result("pages.create", data).__dict__
        else:
            result = get_pages_service().create(data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "page", "update")
@app.command(name="update")
# --------------------------------
# Function Description:
# Updates a Notion page through Core or prints dry-run payload.
# Inputs/Outputs:
# Input page_id, payload, and dry-run flag; output is update response or dry-run result.
# Usage:
# nilo page update PAGE_ID --payload '{"properties": {}}'
# --------------------------------
def update_page(
    page_id: str,
    payload: str = typer.Option(..., "--payload", help="JSON payload for pages.update"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    resolved_page_id = parse_notion_page_id(page_id)
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("pages.update", {"page_id": resolved_page_id, **data}).__dict__
    else:
        try:
            result = get_pages_service().update(resolved_page_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "page", "trash")
@app.command(name="trash")
# --------------------------------
# Function Description:
# Moves a page to trash through Core or prints dry-run payload.
# Inputs/Outputs:
# Input page_id and dry-run flag; output is trash response or dry-run result.
# Usage:
# nilo page trash PAGE_ID --dry-run
# --------------------------------
def trash_page(
    page_id: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    resolved_page_id = parse_notion_page_id(page_id)
    if dry_run:
        result = dry_run_result("pages.trash", {"page_id": resolved_page_id}).__dict__
    else:
        try:
            result = get_pages_service().trash(resolved_page_id)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)
