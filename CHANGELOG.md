# Changelog

All notable changes to N.I.L.O. are documented in this file.

## Unreleased

## 0.4.0 - 2026-07-12

### Added

- Added a shared `runtime` layer for MCP server process state, logs, and stdio/Streamable HTTP lifecycle behavior.
- Added explicit CLI aliases of at most six letters and stable JSON usage errors for Function Calling.
- Added global/project configuration location resolution, project-level non-sensitive overrides, and Git-like upward project discovery.
- Added regression coverage for shared service providers, configuration boundaries, command aliases, JSON errors, and MCP server lifecycle behavior.

### Changed

- Moved reusable business behavior into `core` and reusable execution behavior into `runtime`, keeping CLI and MCP modules as thin adapters.
- Made project configuration take precedence over global settings while keeping credentials in global configuration only.
- Made project initialization create or incrementally update `.gitignore` with the `.notion_mcp/` entry without replacing existing content.
- Standardized MCP transports on `stdio` for local command-launched clients and `streamable-http` for URL-based local or remote clients.
- Updated the English, Japanese, and Chinese documentation for the new architecture, CLI, configuration, and MCP transport contracts.
- Upgraded GitHub Actions to current Node.js 24-compatible major releases while preserving CI, Pages, and PyPI Trusted Publishing behavior.
- Updated locked dependencies to patched releases after a clean pre-release vulnerability audit.
- Hardened MCP secret redaction and required explicit confirmation for destructive Raw API operations.

### Removed

- Removed legacy SSE transport support from the supported MCP transport contract.
- Removed old root CLI entrypoints from the public command surface; compatibility-only entries remain hidden where required.
