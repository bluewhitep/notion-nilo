# Architecture Overview

This document defines the implementation boundaries for the current N.I.L.O. repository.

## Goal

N.I.L.O. provides a local Notion MCP server with two shared implementation layers and two thin adapters:

- Core: the single business logic layer.
- Runtime: shared process and execution lifecycle behavior that is not business logic.
- CLI: the git-like local command interface for humans.
- MCP server/tools: the structured Agent/LLM adapter.

User installation, Notion connection setup, and command usage live under `Docs/EN/User/`. This developer section documents implementation boundaries.

## Target Structure

```text
Human / Function Calling -> CLI adapter -> Core / Runtime
Agent / LLM -> MCP adapter -> Core / Runtime
```

Required:

```text
CLI -> Core
CLI -> Runtime
MCP Tool -> Core
MCP Tool -> Runtime
```

Forbidden:

```text
CLI -> MCP
MCP -> CLI
Core or Runtime -> CLI or MCP
CLI -> Notion SDK
MCP Tool -> Notion SDK
```

## Core

Core is the only business logic layer. It owns:

- Global configuration reads/writes, project context resolution, and token redaction.
- Centralized Notion API version, timeout, and retry handling.
- Notion SDK-compatible client creation.
- Auth validation and user/bot identity lookup.
- Domain services for:
  - pages
  - blocks
  - databases
  - data sources
  - users
  - comments
  - views
  - file uploads
  - search
  - custom emojis
- The Raw API registry and controlled fallback calls.
- Local audit records and a shared error model.

Core also owns global/project configuration composition. The effective configuration loads global credentials first, then applies only credential-free project overrides from the nearest project below the user home. Project settings take precedence over global settings; tokens and other credentials remain global-only.

## Runtime

Runtime contains shared non-domain execution behavior, including managed server process state, log paths, background Streamable HTTP lifecycle, and foreground stdio process startup. CLI and MCP adapters may import Runtime; Runtime must not import either adapter.

## CLI

The CLI is the human entrypoint. It owns:

- Git-like command structure.
- Human-readable output.
- `--json` output, including one-line stable usage-error envelopes for Function Calling.
- Explicit alphabetic short aliases of at most six characters for public commands.
- `--dry-run` previews.
- Local MCP server lifecycle commands.

Public server commands include:

```text
nilo server run
nilo server status
nilo server stop
nilo server logs
nilo server remove
nilo server stdio
```

CLI resource commands call Core services for Notion operations and Runtime for process lifecycle. CLI must not import the MCP adapter.

The project-local `.notion_mcp/` directory stores project context, attachment state, and credential-free setting overrides. It does not store tokens. Global configuration stores credentials. Project discovery walks upward only to the user home; the home-level `.notion_mcp/` is global-only. Project initialization incrementally adds `.notion_mcp/` to the project root `.gitignore`.

## MCP Tool

MCP tools are the Agent/LLM entrypoint. They own:

- Tool inventory.
- Input schemas.
- Tool annotations.
- Structured errors.
- Confirmation requirements for dangerous operations.

MCP tools call Core services directly. They do not construct CLI command strings.

Supported transports are `stdio` for a local command-launched client and `streamable-http` for a URL-based service/client connection. Legacy SSE is not supported. Remote deployment, authentication, TLS, and reverse-proxy configuration are intentionally deferred; current server examples are local-only.

## Non-Functional Boundaries

- Tokens must not appear in normal CLI output or MCP configuration status.
- CLI and MCP write operations must support dry-run previews or dangerous-operation confirmation where appropriate.
- Live tests are skipped by default and must run only against explicit test pages, databases, data sources, or workspaces.
- Notion-Version is managed by Core configuration and must not be scattered through CLI, MCP tools, or individual services.
- Shared behavior belongs under Core or Runtime. CLI and MCP modules may define only adapter-specific behavior.
