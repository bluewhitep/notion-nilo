# File: src/notion_mcp/cli/commands/server.py
# Format: UTF-8
# =============================
# File Description:
# CLI commands for managing the local MCP server lifecycle.
# TAG: cli, server, lifecycle
# =============================

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import typer

from notion_mcp.cli.formatting import echo_json
from notion_mcp.mcp_server.process_manager import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_TRANSPORT,
    ServerProcessError,
    get_server_status,
    read_server_logs,
    remove_server_state,
    start_background_server,
    stop_background_server,
)
from notion_mcp.mcp_server.server import serve as serve_foreground

app = typer.Typer(add_completion=False, help="Manage the local MCP server")


# --------------------------------
# Function Description:
# Registers server lifecycle commands and the serve alias.
# Inputs/Outputs:
# Input root Typer app; output is app with server subcommands.
# Usage:
# register(root_app)
# --------------------------------
def register(root_app: typer.Typer) -> None:
    root_app.add_typer(app, name="server")
    root_app.add_typer(app, name="serve", hidden=True)


# --------------------------------
# Function Description:
# Prints runtime errors in text or JSON mode and exits non-zero.
# Inputs/Outputs:
# Input exception and output mode; raises typer.Exit.
# Usage:
# exit_runtime_error(error, json_output=True)
# --------------------------------
def exit_runtime_error(error: ServerProcessError, *, json_output: bool = False) -> None:
    if json_output:
        echo_json({"ok": False, "error": {"code": "server_process_error", "message": str(error)}})
    else:
        typer.echo(f"Error: {error}")
    raise typer.Exit(code=1)


# --------------------------------
# Function Description:
# Wraps a status payload in the CLI JSON response envelope.
# Inputs/Outputs:
# Input status payload; returns JSON-ready response dictionary.
# Usage:
# response = server_response(status)
# --------------------------------
def server_response(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "server": payload}


# --------------------------------
# Function Description:
# Starts a detached streamable-http MCP server process.
# Inputs/Outputs:
# Input host, port, and optional log path; output is server state.
# Usage:
# notion-mcp server run --host 127.0.0.1 --port 8000
# --------------------------------
@app.command(name="run")
def run_command(
    host: str = typer.Option(DEFAULT_HOST, "--host", help="Bind address"),
    port: int = typer.Option(DEFAULT_PORT, "--port", help="Bind port"),
    log_file: Path | None = typer.Option(None, "--log-file", help="Write server output to this file"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        state = start_background_server(
            host=host,
            port=port,
            transport=DEFAULT_TRANSPORT,
            log_file=log_file,
        )
    except ServerProcessError as exc:
        exit_runtime_error(exc, json_output=json_output)
    payload = state.to_dict()
    payload["running"] = True
    if json_output:
        echo_json(server_response(payload))
        return
    typer.echo("Server started")
    typer.echo(f"PID: {state.pid}")
    typer.echo(f"Transport: {state.transport}")
    typer.echo(f"URL: {state.url}")
    typer.echo(f"State file: {state.state_file}")
    typer.echo(f"Log file: {state.log_file}")


# --------------------------------
# Function Description:
# Runs a foreground stdio MCP server for command-based MCP clients.
# Inputs/Outputs:
# No input; blocks until the parent client exits or the user presses Ctrl+C.
# Usage:
# notion-mcp server stdio
# --------------------------------
@app.command(name="stdio")
def stdio_command() -> None:
    serve_foreground(transport="stdio")


# --------------------------------
# Function Description:
# Shows the managed background server status.
# Inputs/Outputs:
# Optional JSON flag; output is human text or JSON.
# Usage:
# notion-mcp server status --json
# --------------------------------
@app.command(name="status")
def status_command(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        status = get_server_status()
    except ServerProcessError as exc:
        exit_runtime_error(exc, json_output=json_output)
    if json_output:
        echo_json(server_response(status))
        return
    if status.get("running"):
        typer.echo("Server is running")
        typer.echo(f"PID: {status['pid']}")
        typer.echo(f"Transport: {status['transport']}")
        typer.echo(f"URL: {status['url']}")
        typer.echo(f"Log file: {status['log_file']}")
        return
    typer.echo(f"Server is not running ({status['status']})")
    typer.echo(f"State file: {status['state_file']}")
    typer.echo(f"Log file: {status['log_file']}")


# --------------------------------
# Function Description:
# Stops the managed background server process.
# Inputs/Outputs:
# Input timeout and force flag; output is final status.
# Usage:
# notion-mcp server stop --timeout 10
# --------------------------------
@app.command(name="stop")
def stop_command(
    timeout: float = typer.Option(10, "--timeout", help="Seconds to wait for graceful stop"),
    force: bool = typer.Option(False, "--force", help="Kill the process if it does not stop gracefully"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        status = stop_background_server(timeout_seconds=timeout, force=force)
    except ServerProcessError as exc:
        exit_runtime_error(exc, json_output=json_output)
    if json_output:
        echo_json(server_response(status))
        return
    if status.get("status") == "not_found":
        typer.echo("Server is not running")
        return
    typer.echo("Server stopped")
    typer.echo(f"PID: {status['pid']}")
    typer.echo(f"State file: {status['state_file']}")


# --------------------------------
# Function Description:
# Removes managed server state and logs after stopping the process if needed.
# Inputs/Outputs:
# Input cleanup flags; output is removed file list.
# Usage:
# notion-mcp server remove
# --------------------------------
@app.command(name="remove")
def remove_command(
    keep_log: bool = typer.Option(False, "--keep-log", help="Keep the log file"),
    force: bool = typer.Option(False, "--force", help="Force stop before removing state"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        result = remove_server_state(keep_log=keep_log, force=force)
    except ServerProcessError as exc:
        exit_runtime_error(exc, json_output=json_output)
    if json_output:
        echo_json(server_response(result))
        return
    typer.echo("Server state removed")
    for removed in result["removed"]:
        typer.echo(f"Removed: {removed}")


# --------------------------------
# Function Description:
# Prints the managed server log file.
# Inputs/Outputs:
# Input tail and follow options; output is log text.
# Usage:
# notion-mcp server logs --tail 100
# --------------------------------
@app.command(name="logs")
def logs_command(
    tail: int = typer.Option(50, "--tail", help="Number of trailing lines to print; use 0 for all"),
    follow: bool = typer.Option(False, "--follow", help="Continue printing new log lines"),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output"),
) -> None:
    try:
        logs = read_server_logs(tail=tail)
    except ServerProcessError as exc:
        exit_runtime_error(exc, json_output=json_output)
    if json_output:
        echo_json({"ok": True, "logs": logs})
        return
    typer.echo(f"Log file: {logs['log_file']}")
    if logs["text"]:
        typer.echo(logs["text"])
    if not follow:
        return
    log_path = Path(logs["log_file"])
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as handle:
            handle.seek(0, 2)
            while True:
                line = handle.readline()
                if line:
                    typer.echo(line.rstrip("\n"))
                else:
                    time.sleep(0.5)
    except KeyboardInterrupt:
        return
