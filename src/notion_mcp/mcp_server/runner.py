# File: src/notion_mcp/mcp_server/runner.py
# Format: UTF-8
# =============================
# File Description:
# Subprocess entrypoint used by the CLI background server manager.
# TAG: mcp, server, runner
# =============================

from __future__ import annotations

import argparse

from notion_mcp.mcp_server.server import serve


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
    parser.add_argument("--transport", default="streamable-http", choices=["streamable-http", "stdio"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


# --------------------------------
# Function Description:
# Starts the MCP server process with parsed arguments.
# Inputs/Outputs:
# No input; blocks until the server exits.
# Usage:
# python -m notion_mcp.mcp_server.runner --host 127.0.0.1 --port 8000
# --------------------------------
def main() -> None:
    args = parse_args()
    serve(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
