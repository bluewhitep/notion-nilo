# Project Config CLI

This page covers project context and configuration commands.

## Commands

| Command | Purpose |
| --- | --- |
| `nilo init` | Create project-local `.notion_mcp/` context in the current directory. |
| `nilo pwd` | Resolve the current project root by walking upward from the current directory. |
| `nilo version` | Show the package version and configured Notion API version. |
| `nilo config --global --show` | Show global configuration status without revealing the token. |
| `nilo config --global user.token <token>` | Set the user-level Notion token. |
| `nilo config --global user.name <name>` | Set the user-level display name. |
| `nilo config --local --show` | Show project-local configuration for the current directory tree. |

## Examples

```bash
nilo init --project-name "Demo"
nilo pwd
nilo version --json
nilo config --global user.token ntn_xxx
nilo config --global user.name "Ada"
nilo config --global --show
nilo config --local --show --json
```

Global configuration stores the token and runtime settings. Project-local configuration does not store the token. Most users do not need to set `user_id`; run `nilo auth whoami --json` when you need to inspect the current token identity.

## Paths and Precedence

- Global directory: `~/.notion_mcp/`; global file: `~/.notion_mcp/config.json`. `NOTION_MCP_CONFIG` may select another global file.
- Project directory: `<project-root>/.notion_mcp/`; project file: `<project-root>/.notion_mcp/config.json`.
- Effective non-sensitive settings use project values before global values.
- Project overrides are limited to `notion_version`, `timeout_ms`, `retry`, `default_transport`, and `audit_enabled`.
- Tokens and other credentials are global-only and are never read from project configuration.

## Upward Location Lookup

When the current directory is inside the user-home tree, the location API walks upward to the home but does not consider the home itself a project. The nearest `.notion_mcp/config.json` below it is the project configuration; the home-level `.notion_mcp/` is global-only.

When a workspace is outside the home tree, such as on an external disk or mounted directory, project lookup walks toward that filesystem root so Git-like project commands still work. The filesystem root itself is never considered a project. Global lookup does not follow this external path: it still uses only the user home or `NOTION_MCP_CONFIG`.

The result reports the two locations independently:

- no project file: `project_dir=None`;
- no global file, including when `~/.notion_mcp/config.json` is absent: `global_dir=None`;
- only a home-level global file: `project_dir=None` and `global_dir=~/.notion_mcp`.

## Initialization and Git Ignore

`nilo init` cannot initialize the user home as a project. In a valid project root it creates `.notion_mcp/`, creates the root `.gitignore` if needed, and incrementally adds the exact `.notion_mcp/` line. Existing `.gitignore` content is preserved, and repeated initialization does not duplicate the entry.
