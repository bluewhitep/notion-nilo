# File: src/nilo/cli/commands/blocks.py
# Format: UTF-8
# =============================
# File Description:
# CLI block commands backed by Core block service.
# TAG: cli, blocks
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError
from nilo.core.models import dry_run_result

from ..aliases import add_group_alias, command_alias
from ..core_services import get_blocks_service as _get_blocks_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="Block operations")


# --------------------------------
# Function Description:
# Registers block command aliases.
# Inputs/Outputs:
# Input root Typer app; output is app with block/blocks subcommands.
# Usage:
# register(root_app)
# --------------------------------
def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="block")
    add_group_alias(root_app, app, "block")
    root_app.add_typer(app, name="blocks", hidden=True)


# --------------------------------
# Function Description:
# Returns the Core blocks service.
# Inputs/Outputs:
# No input; returns BlocksService.
# Usage:
# get_blocks_service().list_children("block-id")
# --------------------------------
def get_blocks_service():
    return _get_blocks_service()


@command_alias(app, "block", "children")
@app.command(name="children")
# --------------------------------
# Function Description:
# Lists child blocks through Core.
# Inputs/Outputs:
# Input block_id and JSON flag; output is children list response.
# Usage:
# nilo block children BLOCK_ID --json
# --------------------------------
def children(
    block_id: str,
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        result = get_blocks_service().list_children(block_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "block", "append")
@app.command(name="append")
# --------------------------------
# Function Description:
# Appends child blocks through Core or prints dry-run payload.
# Inputs/Outputs:
# Input block_id and JSON payload; output is append response or dry-run result.
# Usage:
# nilo block append BLOCK_ID --payload '{"children": []}' --dry-run
# --------------------------------
def append(
    block_id: str,
    payload: str = typer.Option(..., "--payload", help="JSON payload with children/position"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(payload)
    children_payload = data.get("children", [])
    children_list = children_payload if isinstance(children_payload, list) else []
    position = data.get("position")
    if dry_run:
        result = dry_run_result("blocks.children.append", {"block_id": block_id, **data}).__dict__
    else:
        try:
            result = get_blocks_service().append_children(
                block_id,
                children=children_list,
                position=position if isinstance(position, dict) else None,
            )
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "block", "insert-after")
@app.command(name="insert-after")
# --------------------------------
# Function Description:
# Inserts block children after an existing sibling block.
# Inputs/Outputs:
# Input target block id and payload; output is append result or dry-run payload.
# Usage:
# nilo block insert-after BLOCK_ID --payload '{"children": []}'
# --------------------------------
def insert_after(
    block_id: str,
    payload: str = typer.Option(..., "--payload", help="JSON payload with children"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    data = parse_json_object(payload)
    children_list = _children_from_payload(data)
    position = {"type": "after_block", "after_block": {"id": block_id}}
    if dry_run:
        result = dry_run_result("blocks.children.append", {"after": block_id, "position": position, **data}).__dict__
    else:
        try:
            target = get_blocks_service().retrieve(block_id)
            parent_id = _parent_id_for_append(target)
            result = get_blocks_service().append_children(parent_id, children=children_list, position=position)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    if json_output:
        echo_json(result)
    else:
        typer.echo(result)


@command_alias(app, "block", "update")
@app.command(name="update")
# --------------------------------
# Function Description:
# Updates a block through Core or prints dry-run payload.
# Inputs/Outputs:
# Input block id and JSON payload; output is update result or dry-run result.
# Usage:
# nilo block update BLOCK_ID --payload '{"paragraph": {}}'
# --------------------------------
def update(
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


@command_alias(app, "block", "trash")
@app.command(name="trash")
# --------------------------------
# Function Description:
# Moves a block to trash through Core or prints dry-run payload.
# Inputs/Outputs:
# Input block id; output is trash result or dry-run result.
# Usage:
# nilo block trash BLOCK_ID --json
# --------------------------------
def trash(
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


@app.command(name="remove", hidden=True)
# --------------------------------
# Function Description:
# Hidden compatibility alias for block trash.
# Inputs/Outputs:
# Input block id; delegates to trash.
# Usage:
# nilo block remove BLOCK_ID
# --------------------------------
def remove(
    block_id: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not call Notion"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    trash(block_id=block_id, dry_run=dry_run, json_output=json_output)


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
