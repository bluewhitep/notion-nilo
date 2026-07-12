# MCP Clients

This document explains how to connect MCP-compatible tools to the local N.I.L.O. MCP server.

## Configure the Notion Token First

MCP clients do not need to store the Notion token directly. Save the token in the local global configuration:

```bash
nilo config --global user.token ntn_xxx
nilo config --global user.name "Ada"
nilo config --global --show
```

The MCP client only needs to connect to a local `nilo` server.

## Choose a Transport

N.I.L.O. supports exactly these two transports:

| Transport | Best for | Start server manually first |
| --- | --- | --- |
| stdio | Local clients that launch a command with arguments | No |
| streamable-http | Local or remote clients that connect to an MCP service URL | Yes, the service must be running |

Use stdio for a local command-launched client. Use Streamable HTTP when N.I.L.O. runs as a service and the client connects by URL, whether that client is local or remote. Legacy SSE is not supported and `sse` is rejected as a transport value.

## Stdio Configuration

In stdio mode, the MCP client starts and stops the server process.

Use these values:

| Field | Value |
| --- | --- |
| Server name | `nilo` |
| Transport | `stdio` |
| Command | `nilo` |
| Arguments | `server`, `stdio` |

Common JSON shape:

```json
{
  "mcpServers": {
    "nilo": {
      "command": "nilo",
      "args": ["server", "stdio"]
    }
  }
}
```

If the client expects a single command line, use:

```text
nilo server stdio
```

If `nilo` was installed with `uv tool install .`, make sure the shell can run:

```bash
nilo --help
```

If the client cannot find `nilo`, run:

```bash
uv tool update-shell
```

Then restart the terminal or MCP client.

## Stdio Without Installing nilo

If `nilo` is not installed on `PATH`, the client can run it through `uv` from the repository path.

Use these values:

| Field | Value |
| --- | --- |
| Server name | `nilo` |
| Transport | `stdio` |
| Command | `uv` |
| Arguments | `run`, `--no-project`, `--with`, `/path/to/notion-nilo`, `nilo`, `server`, `stdio` |

JSON example:

```json
{
  "mcpServers": {
    "nilo": {
      "command": "uv",
      "args": [
        "run",
        "--no-project",
        "--with",
        "/path/to/notion-nilo",
        "nilo",
        "server",
        "stdio"
      ]
    }
  }
}
```

Replace `/path/to/notion-nilo` with the repository root on your machine.

## Streamable HTTP Configuration

For clients that support an MCP URL or streamable HTTP transport, start the local server:

```bash
nilo server run --host 127.0.0.1 --port 8000
```

Check the status:

```bash
nilo server status
```

Use these client values:

| Field | Value |
| --- | --- |
| Server name | `nilo` |
| Transport | `streamable-http` |
| URL | `http://127.0.0.1:8000/mcp` |
| Authentication | None (localhost example only) |

Common JSON shape:

```json
{
  "mcpServers": {
    "nilo": {
      "transport": "streamable-http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

If the client uses labels such as `http`, `streamableHttp`, or `remote server`, choose the option that accepts a URL and enter:

```text
http://127.0.0.1:8000/mcp
```

Do not put the Notion token into the MCP client. The local `nilo` server reads it from local configuration.

## Remote Service Scope

The transport contract for a remotely deployed N.I.L.O. service is Streamable HTTP at its `/mcp` endpoint; a remote client must not select legacy SSE. This release documents and validates only the localhost server shown above. Remote deployment, authentication, TLS, and reverse-proxy configuration are deferred, so do not expose this unauthenticated localhost example to a network.

## Background Server Management

Check status:

```bash
nilo server status
```

Read logs:

```bash
nilo server logs --tail 100
```

Stop the server:

```bash
nilo server stop
```

Remove local server state and logs:

```bash
nilo server remove
```

Force cleanup when a process is still running:

```bash
nilo server remove --force
```

This only cleans local server runtime state. To remove MCP client entries, uninstall the command, delete local token configuration, or delete project context, see [Uninstallation](Uninstallation.md).

## Environment Variables

If you use a custom global configuration file, pass the same environment variable to the MCP client:

```text
NOTION_MCP_CONFIG=/path/to/config.json
```

Stdio JSON example:

```json
{
  "mcpServers": {
    "nilo": {
      "command": "nilo",
      "args": ["server", "stdio"],
      "env": {
        "NOTION_MCP_CONFIG": "/path/to/config.json"
      }
    }
  }
}
```

## Current MCP Tool Inventory

Configuration and authentication:

- `config_status`
- `config_get`
- `auth_validate`
- `auth_whoami`

Pages:

- `page_retrieve`
- `page_property_retrieve`
- `page_create`
- `page_update`
- `page_trash`

Blocks:

- `block_children_list`
- `block_append`
- `block_update`
- `block_trash`

Databases:

- `database_retrieve`
- `database_query`
- `database_create`
- `database_update`

Data sources:

- `data_source_retrieve`
- `data_source_query`
- `data_source_create`
- `data_source_update`

Users:

- `user_me`
- `user_list`
- `user_retrieve`

Comments:

- `comment_list`
- `comment_create`
- `comment_reply`

Views:

- `view_retrieve`
- `view_list`
- `view_query`
- `view_create`
- `view_update`

File uploads:

- `file_upload_retrieve`
- `file_upload_list`
- `file_upload_create`
- `file_upload_send`
- `file_upload_complete`

Search and custom emoji:

- `search`
- `custom_emoji_list`
- `custom_emoji_retrieve`

Controlled Raw API:

- `raw_api_registered_operations`
- `raw_api_invoke`

## FAQ

If the client does not show N.I.L.O. MCP tools:

1. Run `nilo --help` in a terminal and confirm the command exists.
2. For stdio, confirm `command` and `args` are separate fields.
3. For streamable HTTP, confirm `nilo server status` reports a running server.
4. Check logs with `nilo server logs --tail 100`.
5. Confirm the Notion token is configured with `nilo config --global --show`.

## Security Notes

- The token is stored in a local configuration file.
- Normal status output masks the token.
- MCP client configuration does not need the Notion token.
- The `Authentication: None` example applies only to `127.0.0.1`; remote deployment security is not defined in this release.
- Destructive tools such as `page_trash` and `block_trash` require `confirm=true`.
- Real Notion calls require the connection to be shared with the relevant page, database, or workspace content.
