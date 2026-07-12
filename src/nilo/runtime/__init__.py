# File: src/nilo/runtime/__init__.py
# Format: UTF-8
# =============================
# File Description:
# Public runtime contracts shared by CLI and server adapters.
# TAG: runtime, public-api
# =============================

from .server_process import (
    DEFAULT_HOST,
    DEFAULT_LOG_FILE_NAME,
    DEFAULT_PORT,
    DEFAULT_TRANSPORT,
    RUNTIME_DIR_ENV,
    STATE_FILE_NAME,
    STREAMABLE_HTTP_PATH,
    ServerProcessError,
    ServerRuntimeState,
    build_server_command,
    default_server_log_path,
    get_server_status,
    is_pid_running,
    load_server_state,
    read_server_logs,
    remove_server_state,
    run_foreground_stdio_server,
    runtime_dir_from_env,
    server_state_path,
    start_background_server,
    stop_background_server,
    timestamp_utc,
    wait_for_exit,
    write_json_atomic,
)

__all__ = [
    "DEFAULT_HOST",
    "DEFAULT_LOG_FILE_NAME",
    "DEFAULT_PORT",
    "DEFAULT_TRANSPORT",
    "RUNTIME_DIR_ENV",
    "STATE_FILE_NAME",
    "STREAMABLE_HTTP_PATH",
    "ServerProcessError",
    "ServerRuntimeState",
    "build_server_command",
    "default_server_log_path",
    "get_server_status",
    "is_pid_running",
    "load_server_state",
    "read_server_logs",
    "remove_server_state",
    "run_foreground_stdio_server",
    "runtime_dir_from_env",
    "server_state_path",
    "start_background_server",
    "stop_background_server",
    "timestamp_utc",
    "wait_for_exit",
    "write_json_atomic",
]
