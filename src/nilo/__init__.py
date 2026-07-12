"""
nilo
===============

This package implements the local Notion MCP service, including configuration
management, MCP server setup, CLI commands, and compatibility route modules.

Module overview:

- `config`: Reads and saves global configuration.
- `models`: Contains Pydantic models for validation.
- `routes`: Provides internal REST prototype compatibility routes.
- `mcp_server`: Builds the MCP server and registers tools.
- `cli`: Provides the command-line entry point.

"""

from importlib import metadata

try:
    __version__ = metadata.version("notion-nilo")
except metadata.PackageNotFoundError:
    # Package is not installed; fallback for local development
    __version__ = "0.0.0"

__all__ = ["__version__"]
