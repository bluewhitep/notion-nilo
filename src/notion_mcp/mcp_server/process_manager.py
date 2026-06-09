# File: src/notion_mcp/mcp_server/process_manager.py
# Format: UTF-8
# =============================
# File Description:
# Background process lifecycle helpers for the local MCP server.
# TAG: mcp, server, process, lifecycle
# =============================

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from notion_mcp.core.config import config_path_from_env

RUNTIME_DIR_ENV = "NOTION_MCP_RUNTIME_DIR"
STATE_FILE_NAME = "server.state.json"
DEFAULT_LOG_FILE_NAME = "server.log"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_TRANSPORT = "streamable-http"
STREAMABLE_HTTP_PATH = "/mcp"


class ServerProcessError(RuntimeError):
    """Raised when a managed MCP server process operation cannot be completed."""


@dataclass(frozen=True)
class ServerRuntimeState:
    pid: int
    host: str
    port: int
    transport: str
    url: str
    state_file: str
    log_file: str
    started_at: str
    command: list[str]
    status: str = "running"
    stopped_at: str | None = None

    # --------------------------------
    # Function Description:
    # Converts runtime state to a stable JSON-compatible dictionary.
    # Inputs/Outputs:
    # No input; returns a dictionary with process metadata.
    # Usage:
    # state.to_dict()
    # --------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "host": self.host,
            "port": self.port,
            "transport": self.transport,
            "url": self.url,
            "state_file": self.state_file,
            "log_file": self.log_file,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "status": self.status,
            "command": self.command,
        }

    # --------------------------------
    # Function Description:
    # Builds runtime state from a stored JSON dictionary.
    # Inputs/Outputs:
    # Input raw dictionary; returns ServerRuntimeState or raises ServerProcessError.
    # Usage:
    # ServerRuntimeState.from_dict(raw)
    # --------------------------------
    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ServerRuntimeState":
        try:
            command = raw.get("command") or []
            if not isinstance(command, list):
                command = []
            return cls(
                pid=int(raw["pid"]),
                host=str(raw["host"]),
                port=int(raw["port"]),
                transport=str(raw["transport"]),
                url=str(raw["url"]),
                state_file=str(raw["state_file"]),
                log_file=str(raw["log_file"]),
                started_at=str(raw["started_at"]),
                stopped_at=raw.get("stopped_at"),
                status=str(raw.get("status") or "running"),
                command=[str(part) for part in command],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ServerProcessError("Server state file is invalid") from exc


# --------------------------------
# Function Description:
# Returns an ISO-8601 UTC timestamp for server state files.
# Inputs/Outputs:
# No input; returns a timestamp string.
# Usage:
# timestamp_utc()
# --------------------------------
def timestamp_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# --------------------------------
# Function Description:
# Resolves the runtime directory used for server state and logs.
# Inputs/Outputs:
# Optional runtime directory; returns an expanded Path.
# Usage:
# runtime_dir_from_env()
# --------------------------------
def runtime_dir_from_env(runtime_dir: Path | None = None) -> Path:
    if runtime_dir is not None:
        return runtime_dir.expanduser()
    env_dir = os.getenv(RUNTIME_DIR_ENV)
    if env_dir:
        return Path(env_dir).expanduser()
    return config_path_from_env().expanduser().parent


# --------------------------------
# Function Description:
# Resolves the managed server state file path.
# Inputs/Outputs:
# Optional runtime directory; returns server state Path.
# Usage:
# server_state_path()
# --------------------------------
def server_state_path(runtime_dir: Path | None = None) -> Path:
    return runtime_dir_from_env(runtime_dir) / STATE_FILE_NAME


# --------------------------------
# Function Description:
# Resolves the default managed server log file path.
# Inputs/Outputs:
# Optional runtime directory; returns server log Path.
# Usage:
# default_server_log_path()
# --------------------------------
def default_server_log_path(runtime_dir: Path | None = None) -> Path:
    return runtime_dir_from_env(runtime_dir) / DEFAULT_LOG_FILE_NAME


# --------------------------------
# Function Description:
# Atomically writes a JSON file for runtime state.
# Inputs/Outputs:
# Input path and payload; writes UTF-8 JSON with stable formatting.
# Usage:
# write_json_atomic(path, {"pid": 1})
# --------------------------------
def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)
    os.chmod(path, 0o600)


# --------------------------------
# Function Description:
# Loads stored server runtime state if it exists.
# Inputs/Outputs:
# Optional runtime directory; returns state or None.
# Usage:
# load_server_state()
# --------------------------------
def load_server_state(runtime_dir: Path | None = None) -> ServerRuntimeState | None:
    path = server_state_path(runtime_dir)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ServerProcessError("Server state file is not valid JSON") from exc
    if not isinstance(raw, dict):
        raise ServerProcessError("Server state file must contain a JSON object")
    return ServerRuntimeState.from_dict(raw)


# --------------------------------
# Function Description:
# Checks whether a process id is currently running.
# Inputs/Outputs:
# Input pid; returns True when the process exists.
# Usage:
# is_pid_running(1234)
# --------------------------------
def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# --------------------------------
# Function Description:
# Waits for a pid to exit within a timeout.
# Inputs/Outputs:
# Input pid and timeout seconds; returns True if the process exited.
# Usage:
# wait_for_exit(pid, timeout_seconds=5)
# --------------------------------
def wait_for_exit(pid: int, timeout_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not is_pid_running(pid):
            return True
        time.sleep(0.1)
    return not is_pid_running(pid)


# --------------------------------
# Function Description:
# Builds the Python command used to launch the background MCP server runner.
# Inputs/Outputs:
# Input host, port, and transport; returns argv list.
# Usage:
# build_server_command("127.0.0.1", 8000, "streamable-http")
# --------------------------------
def build_server_command(host: str, port: int, transport: str) -> list[str]:
    return [
        sys.executable,
        "-m",
        "notion_mcp.mcp_server.runner",
        "--transport",
        transport,
        "--host",
        host,
        "--port",
        str(port),
    ]


# --------------------------------
# Function Description:
# Starts the MCP server as a detached background process.
# Inputs/Outputs:
# Input host, port, runtime/log options; returns saved runtime state.
# Usage:
# start_background_server(host="127.0.0.1", port=8000)
# --------------------------------
def start_background_server(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    transport: str = DEFAULT_TRANSPORT,
    runtime_dir: Path | None = None,
    log_file: Path | None = None,
) -> ServerRuntimeState:
    if transport != DEFAULT_TRANSPORT:
        raise ServerProcessError("Background server only supports streamable-http transport")

    resolved_runtime_dir = runtime_dir_from_env(runtime_dir)
    resolved_runtime_dir.mkdir(parents=True, exist_ok=True)
    state_path = server_state_path(resolved_runtime_dir)
    existing = load_server_state(resolved_runtime_dir)
    if existing and is_pid_running(existing.pid):
        raise ServerProcessError(f"Server is already running with PID {existing.pid}")

    resolved_log_file = (log_file.expanduser() if log_file else default_server_log_path(resolved_runtime_dir)).resolve()
    resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
    command = build_server_command(host, port, transport)
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env[RUNTIME_DIR_ENV] = str(resolved_runtime_dir)

    with resolved_log_file.open("ab") as log_handle:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            cwd=Path.cwd(),
            env=env,
            start_new_session=True,
        )
        time.sleep(0.2)
        if process.poll() is not None:
            raise ServerProcessError(f"Server process exited early with code {process.returncode}")

    url = f"http://{host}:{port}{STREAMABLE_HTTP_PATH}"
    state = ServerRuntimeState(
        pid=process.pid,
        host=host,
        port=port,
        transport=transport,
        url=url,
        state_file=str(state_path),
        log_file=str(resolved_log_file),
        started_at=timestamp_utc(),
        command=command,
    )
    write_json_atomic(state_path, state.to_dict())
    return state


# --------------------------------
# Function Description:
# Returns current managed server status from state and process liveness.
# Inputs/Outputs:
# Optional runtime directory; returns a status dictionary.
# Usage:
# get_server_status()
# --------------------------------
def get_server_status(runtime_dir: Path | None = None) -> dict[str, Any]:
    resolved_runtime_dir = runtime_dir_from_env(runtime_dir)
    state_path = server_state_path(resolved_runtime_dir)
    state = load_server_state(resolved_runtime_dir)
    if state is None:
        return {
            "running": False,
            "status": "not_found",
            "runtime_dir": str(resolved_runtime_dir),
            "state_file": str(state_path),
            "log_file": str(default_server_log_path(resolved_runtime_dir)),
        }
    running = is_pid_running(state.pid)
    payload = state.to_dict()
    payload["running"] = running
    payload["runtime_dir"] = str(resolved_runtime_dir)
    if not running and payload.get("status") == "running":
        payload["status"] = "stale"
    return payload


# --------------------------------
# Function Description:
# Stops the managed background MCP server if it is running.
# Inputs/Outputs:
# Input timeout and force flag; returns updated status dictionary.
# Usage:
# stop_background_server(timeout_seconds=5)
# --------------------------------
def stop_background_server(
    *,
    runtime_dir: Path | None = None,
    timeout_seconds: float = 10,
    force: bool = False,
) -> dict[str, Any]:
    resolved_runtime_dir = runtime_dir_from_env(runtime_dir)
    state = load_server_state(resolved_runtime_dir)
    if state is None:
        return get_server_status(resolved_runtime_dir)

    if is_pid_running(state.pid):
        try:
            os.kill(state.pid, signal.SIGTERM)
        except PermissionError as exc:
            raise ServerProcessError(f"Permission denied while stopping server PID {state.pid}") from exc
        if not wait_for_exit(state.pid, timeout_seconds):
            if not force:
                raise ServerProcessError(f"Server PID {state.pid} did not stop within {timeout_seconds:g}s")
            try:
                os.kill(state.pid, signal.SIGKILL)
            except PermissionError as exc:
                raise ServerProcessError(f"Permission denied while killing server PID {state.pid}") from exc
            if not wait_for_exit(state.pid, 3):
                raise ServerProcessError(f"Server PID {state.pid} could not be killed")

    stopped = ServerRuntimeState(
        pid=state.pid,
        host=state.host,
        port=state.port,
        transport=state.transport,
        url=state.url,
        state_file=state.state_file,
        log_file=state.log_file,
        started_at=state.started_at,
        stopped_at=timestamp_utc(),
        status="stopped",
        command=state.command,
    )
    write_json_atomic(server_state_path(resolved_runtime_dir), stopped.to_dict())
    return get_server_status(resolved_runtime_dir)


# --------------------------------
# Function Description:
# Removes managed server state and optionally its log file after stopping the server.
# Inputs/Outputs:
# Input cleanup options; returns removed file paths and final running state.
# Usage:
# remove_server_state(keep_log=False)
# --------------------------------
def remove_server_state(
    *,
    runtime_dir: Path | None = None,
    keep_log: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    resolved_runtime_dir = runtime_dir_from_env(runtime_dir)
    state = load_server_state(resolved_runtime_dir)
    status_before = get_server_status(resolved_runtime_dir)
    log_path = Path(state.log_file) if state else default_server_log_path(resolved_runtime_dir)
    if state and is_pid_running(state.pid):
        stop_background_server(runtime_dir=resolved_runtime_dir, force=force)

    removed: list[str] = []
    state_path = server_state_path(resolved_runtime_dir)
    if state_path.exists():
        state_path.unlink()
        removed.append(str(state_path))
    if not keep_log and log_path.exists():
        log_path.unlink()
        removed.append(str(log_path))
    return {
        "running": False,
        "status": "removed",
        "runtime_dir": str(resolved_runtime_dir),
        "removed": removed,
        "previous": status_before,
    }


# --------------------------------
# Function Description:
# Reads the managed server log file and returns the requested trailing lines.
# Inputs/Outputs:
# Input optional line count; returns log text and metadata.
# Usage:
# read_server_logs(tail=50)
# --------------------------------
def read_server_logs(*, runtime_dir: Path | None = None, tail: int = 50) -> dict[str, Any]:
    resolved_runtime_dir = runtime_dir_from_env(runtime_dir)
    state = load_server_state(resolved_runtime_dir)
    log_path = Path(state.log_file) if state else default_server_log_path(resolved_runtime_dir)
    if not log_path.exists():
        raise ServerProcessError(f"Server log file does not exist: {log_path}")
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    selected = lines[-tail:] if tail > 0 else lines
    return {
        "log_file": str(log_path),
        "tail": tail,
        "lines": selected,
        "text": "\n".join(selected),
    }
