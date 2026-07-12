# CLI Overview

This page summarizes global CLI behavior.

## Common Rules

- `-h` and `--help` are equivalent, for example `nilo -h` and `nilo page -h`.
- Most read commands support `--json` for scripts and agents.
- Commands with side effects, such as write, update, send, complete, and trash commands, should be previewed with `--dry-run` when available.
- JSON input is passed through `--payload`, `--properties`, or `--arguments`. The value must be a JSON object.
- Plural forms such as `page/pages`, `block/blocks`, and `database/databases` are aliases. User documentation uses the singular form by default.
- Like Git or gh, global commands work from any directory while project commands use the nearest `.notion_mcp/` found by walking upward to the user home.
- Before real Notion calls, set a global token with `nilo config --global user.token <token>` and share the target content with the Notion connection.

## Short Aliases

Every public command also has an explicit alphabetic short alias of at most six characters. Canonical names remain the primary documentation form. Examples:

```bash
nilo cfg --global --show
nilo pg get <page_id> --json
nilo srv start --host 127.0.0.1 --port 8000
```

Common root aliases include `init/ini`, `version/ver`, `config/cfg`, `pwd/cwd`, `page/pg`, `block/blk`, `database/db`, `data-source/ds`, and `server/srv`.

## Function Calling JSON Errors

For Function Calling, include `--json`. If an option is unknown or a required/valid parameter is missing, the CLI writes exactly one compact JSON line with a stable error code instead of Rich help output. Calls without `--json` retain normal human-readable help and errors.

```json
{"ok":false,"error":{"type":"CliUsageError","code":"cli_missing_parameter","message":"...","details":{"exit_code":2}}}
```

## JSON Input Examples

```bash
nilo page update <page_id> --payload '{"properties": {}}'
nilo database query --payload '{"page_size": 10}'
nilo raw-api invoke search --arguments '{"query": "Tasks"}' --json
```

## Preview Side Effects

```bash
nilo block append <block_id> --payload '{"children": []}' --dry-run --json
nilo block trash <block_id> --dry-run
```
