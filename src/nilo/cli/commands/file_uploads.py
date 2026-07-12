# File: src/nilo/cli/commands/file_uploads.py
# Format: UTF-8
# =============================
# File Description:
# CLI file upload commands backed by Core file upload service.
# TAG: cli, file-uploads
# =============================

from __future__ import annotations

import typer

from nilo.core.errors import CoreError
from nilo.core.models import dry_run_result

from ..aliases import add_group_alias, command_alias
from ..core_services import get_file_uploads_service as _get_file_uploads_service
from ..formatting import echo_json, exit_with_error, parse_json_object

app = typer.Typer(add_completion=False, help="File upload operations")


def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="file-upload")
    add_group_alias(root_app, app, "file-upload")
    root_app.add_typer(app, name="file-uploads", hidden=True)
    root_app.add_typer(app, name="files", hidden=True)


def get_file_uploads_service():
    return _get_file_uploads_service()


@command_alias(app, "file-upload", "retrieve")
@app.command(name="retrieve")
def retrieve(file_upload_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    try:
        result = get_file_uploads_service().retrieve(file_upload_id)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "file-upload", "list")
@app.command(name="list")
def list_uploads(
    payload: str = typer.Option("{}", "--payload"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    try:
        result = get_file_uploads_service().list(**data)
    except CoreError as exc:
        exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "file-upload", "create")
@app.command(name="create")
def create(
    payload: str = typer.Option(..., "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("file_uploads.create", data).__dict__
    else:
        try:
            result = get_file_uploads_service().create(data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "file-upload", "send")
@app.command(name="send")
def send(
    file_upload_id: str,
    payload: str = typer.Option(..., "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("file_uploads.send", {"file_upload_id": file_upload_id, **data}).__dict__
    else:
        try:
            result = get_file_uploads_service().send(file_upload_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)


@command_alias(app, "file-upload", "complete")
@app.command(name="complete")
def complete(
    file_upload_id: str,
    payload: str = typer.Option("{}", "--payload"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    data = parse_json_object(payload)
    if dry_run:
        result = dry_run_result("file_uploads.complete", {"file_upload_id": file_upload_id, **data}).__dict__
    else:
        try:
            result = get_file_uploads_service().complete(file_upload_id, data)
        except CoreError as exc:
            exit_with_error(exc, json_output=json_output)
    echo_json(result) if json_output else typer.echo(result)
