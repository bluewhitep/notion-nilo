# notion-mcp

This repository provides a local Notion MCP server with a Core + CLI + MCP Tool architecture.

Current state:

- Core is the only business logic layer.
- CLI is the git-like human entrypoint.
- MCP tools are the structured Agent/LLM entrypoint.
- Background MCP server lifecycle commands are available through `notion-mcp server ...`.

Use `Docs/User/Installation.md` and `Docs/User/MCP_Clients.md` for setup and client configuration.
