# File: src/nilo/cli/commands/comments.py
# Format: UTF-8
# =============================
# File Description:
# CLI comment commands backed by Core comments service.
# TAG: cli, comments
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError
from nilo.core.models import dry_run_result

from ..aliases import add_group_alias, command_alias
from ..core_services import get_comments_service as _get_comments_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="Comment operations")


def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="comment")
    add_group_alias(root_app, app, "comment")
    root_app.add_typer(app, name="comments", hidden=True)


def get_comments_service():
    return _get_comments_service()


@command_alias(app, "comment", "list")
@app.command(name="list")
def list_comments(
    block_id: str | None = typer.Option(None, "--block-id"),
    page_size: int | None = typer.Option(None, "--page-size"),
    start_cursor: str | None = typer.Option(None, "--start-cursor"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    params: dict[str, object] = {}
    if block_id is not None:
        params["block_id"] = block_id
    if page_size is not None:
        params["page_size"] = page_size
    if start_cursor is not None:
        params["start_cursor"] = start_cursor
    try:
        result = get_comments_service().list(**params)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "comment", "create")
@app.command(name="create")
def create(
    payload: str = typer.Option(..., "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("comments.create", data).__dict__
    else:
        try:
            result = get_comments_service().create(data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "comment", "reply")
@app.command(name="reply")
def reply(
    discussion_id: str,
    rich_text: str = typer.Option(..., "--rich-text"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(rich_text)
    rich_text_list = data.get("rich_text", [])
    payload = {"discussion_id": discussion_id, "rich_text": rich_text_list}
    if dry_run:
        result = dry_run_result("comments.reply", payload).__dict__
    else:
        try:
            result = get_comments_service().reply(
                discussion_id,
                rich_text_list if isinstance(rich_text_list, list) else [],
            )
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
