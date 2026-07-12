# CLI API

This document records the current public `nilo` CLI surface, hidden compatibility entries, and Core call boundaries. The CLI owns terminal user experience; business behavior must come from Core services.

## Entrypoint

- Package: `nilo.cli`
- Console script: `nilo = nilo.cli:app`
- Root app: `src/nilo/cli/app.py`
- Help options: `--help` and `-h`

## Core Boundary

```text
CLI -> Core or Runtime
MCP -> Core or Runtime
```

The CLI must not call the Notion SDK or import the MCP adapter. Shared business behavior belongs in Core and shared process/execution behavior belongs in Runtime. Core and Runtime must not import CLI or MCP. When adding a command, first confirm the corresponding shared capability exists; adapter modules may define only CLI-specific parsing, presentation, and interaction.

## Public Root Commands

- `nilo init`
  - Initializes project-local `.notion_mcp/` context.
  - Does not write tokens and does not require a user ID.
- `nilo pwd`
  - Resolves the project root by walking upward from the current directory.
- `nilo version`
  - Prints the package version and configured Notion API version.
- `nilo config --global --show`
  - Prints a redacted global configuration summary.
- `nilo config --global user.token <token>`
  - Updates the global token.
- `nilo config --global user.name <name>`
  - Updates the global display name.
- `nilo config --local --show`
  - Prints the current project-local configuration summary.

`project`, `local`, root `status`, `config global/local`, and `config set/get/unset/list` remain hidden compatibility entries. They are not part of the public command surface.

The CLI follows Git/gh-style scope: global commands work from any directory, while project commands resolve the nearest `.notion_mcp/` context by walking upward to the user home.

## Short Alias Contract

Every public canonical command path has an explicit alphabetic alias of at most six characters. Canonical names remain the documented interface; aliases execute the same callback and are hidden from normal help to keep help concise.

Root examples:

| Canonical | Alias |
| --- | --- |
| `init` | `ini` |
| `version` | `ver` |
| `config` | `cfg` |
| `pwd` | `cwd` |
| `page` | `pg` |
| `block` | `blk` |
| `database` | `db` |
| `data-source` | `ds` |
| `server` | `srv` |

Leaf examples include `retrieve -> get`, `create -> new`, `update -> upd`, `trash -> del`, and `server run -> server start`. The complete validated mapping is defined in `src/nilo/cli/aliases.py`.

## Function Calling Error Contract

When `--json` appears anywhere in an invocation, Click/Typer usage errors are emitted as exactly one compact JSON line. The stable envelope contains `ok=false` and an `error` object with `type`, `code`, `message`, and `details.exit_code`. Stable usage codes include `cli_missing_parameter`, `cli_invalid_parameter`, `cli_unknown_option`, and `cli_usage_error`. Human invocations without `--json` retain normal help and error rendering.

## Project Context

Project context is provided by Core:

```text
ProjectResolver
ProjectConfigStore
AttachmentStore
ContextResolver
```

Resolution order:

```text
explicit id > attached state > error
```

Project-local configuration:

```text
.notion_mcp/config.json
```

Attachment state:

```text
.notion_mcp/state/page.attach.json
.notion_mcp/state/database.attach.json
```

Project-local configuration and attachment state must not store tokens.

Project configuration may override only non-sensitive Core settings. Global credentials always remain global. Project initialization rejects the user home as a project root and incrementally adds `.notion_mcp/` to the root `.gitignore`.

## Page CLI

Page ID inputs are normalized through `src/nilo/core/identifiers.py`. Public `<page_id>` arguments accept raw IDs, copied Notion URLs, and Markdown links that contain Notion URLs.

Public commands:

- `nilo page attach <page_id>` binds the default page for the current project. This is project context binding, not file attachment.
- `nilo page status` shows the attached page.
- `nilo page refresh` refreshes local title, URL, and status without changing the remote page.
- `nilo page detach` deletes local page attachment state without changing the remote page.
- `nilo page retrieve [page_id]` reads page metadata and uses the attached page when no ID is provided.
- `nilo page blocks [page_id]` reads a block summary and uses the attached page when no ID is provided.
- `nilo page create` creates a page and defaults to the attached page as parent when the payload has no parent.
- `nilo page create --parent-page <page_id>` creates a child page under a specific parent.
- `nilo page update <page_id>` updates normal page or data source entry page properties.
- `nilo page trash <page_id>` moves a page to trash.

Hidden compatibility entries remain for old page content/current/deattach aliases, the old page-scoped block group, and the old page insert group. They must not be documented as public user commands.

## Block CLI

Public commands:

- `nilo block children <block_id>`
- `nilo block append <block_id>`
- `nilo block insert-after <block_id>`
- `nilo block update <block_id>`
- `nilo block trash <block_id>`

`insert-before` is not a stable public command. `block remove` is only a hidden compatibility alias for trash behavior.

## Database and DataSource

Semantic model:

```text
database = container
data_source = table under database
page = page or data source entry
block = page content node
```

Use `database` for container-level operations. Use `data-source` for table-level schema, query, templates, and entry creation. Use database shortcuts only for the active data source on the attached database.

### Database Container Commands

- `nilo database attach <database_id>`
- `nilo database attach <database_id> --data-source <id_or_name>`
- `nilo database status`
- `nilo database refresh`
- `nilo database detach`
- `nilo database retrieve [database_id]`
- `nilo database sources [database_id]`
- `nilo database create`
- `nilo database create --parent-page <page_id>`
- `nilo database update <database_id>`
- `nilo database rename <database_id> <new_name>`

`database create` creates a database container and an initial data source. `database update` only updates container-level fields and does not modify data source schema.

### Database Shortcut Commands

These commands operate only on the active data source of the attached database:

- `nilo database query --payload <json>`
- `nilo database page create --properties <json>`
- `nilo database property rename <property> <new_name>`

The public CLI does not expose `database query --data-source`, `database page create <data_source_id>`, `database page update <page_id>`, or a three-argument `database property rename`. Explicit data source operations must use `data-source`; page property updates use `page update`.

### DataSource Commands

- `nilo data-source retrieve <data_source_id>`
- `nilo data-source query <data_source_id>`
- `nilo data-source create`
- `nilo data-source create <database_id>`
- `nilo data-source update <data_source_id>`
- `nilo data-source templates <data_source_id>`
- `nilo data-source property rename <data_source_id> <property> <new_name>`
- `nilo data-source page create <data_source_id>`

## Other Object Domains

- `nilo auth validate`
- `nilo auth whoami`
- `nilo user me/list/retrieve`
- `nilo comment list/create/reply`
- `nilo view retrieve/list/query/create/update`
- `nilo file-upload retrieve/list/create/send/complete`
- `nilo search query`
- `nilo custom-emoji list/retrieve`
- `nilo raw-api operations`
- `nilo raw-api invoke <operation>`
- `nilo server run`
- `nilo server status`
- `nilo server stop`
- `nilo server logs`
- `nilo server remove`
- `nilo server stdio`

Raw API is an advanced fallback entrypoint and should not be the normal path for page or database editing.

## Removed Legacy Entrypoints

These old root commands are no longer public CLI entries:

- `nilo set-token`
- `nilo set-user`
- `nilo show`
- `nilo run`
- `nilo mcp serve`

Use `nilo config --global ...` for configuration and `nilo server ...` for MCP server lifecycle.
