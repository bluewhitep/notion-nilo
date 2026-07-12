# File: src/nilo/mcp_server/runner.py
# Format: UTF-8
# =============================
# File Description:
# Subprocess entrypoint used by the CLI background server manager.
# TAG: mcp, server, runner
# =============================

from __future__ import annotations

import argparse

from nilo.core.config_constants import SUPPORTED_TRANSPORTS
from nilo.mcp_server.server import serve
from nilo.runtime.server_process import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TRANSPORT


# --------------------------------
# Function Description:
# Parses runner command-line arguments.
# Inputs/Outputs:
# No input; returns argparse namespace for the background process.
# Usage:
# parse_args()
# --------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Notion MCP server process")
    parser.add_argument("--transport", default=DEFAULT_TRANSPORT, choices=SUPPORTED_TRANSPORTS)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser.parse_args()


# --------------------------------
# Function Description:
# Starts the MCP server process with parsed arguments.
# Inputs/Outputs:
# No input; blocks until the server exits.
# Usage:
# python -m nilo.mcp_server.runner --host 127.0.0.1 --port 8000
# --------------------------------
def main() -> None:
    args = parse_args()
    serve(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
