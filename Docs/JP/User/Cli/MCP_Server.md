# MCP Server CLI

このページでは local MCP server lifecycle commands を説明します。

## Transport contract

サポートするのは `stdio` と `streamable-http` だけです。local command-launched MCP client は stdio、URL で接続する local/remote MCP client は Streamable HTTP を使います。legacy SSE はサポートしません。

この release が対象とするのは localhost server operation だけです。remote deployment、authentication、TLS、reverse proxy configuration は今回延期しているため、unauthenticated example endpoint を network に公開しないでください。

## Background HTTP Server

| Command | Purpose |
| --- | --- |
| `nilo server run` | streamable HTTP MCP server を background で起動します。 |
| `nilo server status` | server の稼働状態、PID、URL、log path を表示します。 |
| `nilo server stop` | background server process を停止します。 |
| `nilo server logs` | background server logs を読み取ります。 |
| `nilo server remove` | server を停止し local runtime state を削除します。ログはデフォルトで削除されます。 |

デフォルトの local server command:

```bash
nilo server run --host 127.0.0.1 --port 8000
```

MCP URL:

```text
http://127.0.0.1:8000/mcp
```

よく使う管理コマンド:

```bash
nilo server status
nilo server logs --tail 100
nilo server stop
nilo server remove
```

process が正常終了しない場合は force stop します。

```bash
nilo server stop --force
```

## Stdio Server

command-based MCP client が stdio process を起動する場合:

```bash
nilo server stdio
```

この command は foreground で動き、MCP client が閉じるかユーザーが interrupt するまで実行されます。

## Short aliases

Server commands には `server/srv`、`run/start`、`stdio/pipe`、`status/stat`、`stop/halt`、`logs/tail`、`remove/rm` という明示的な short aliases があります。

```bash
nilo srv start --host 127.0.0.1 --port 8000
nilo srv stat
nilo srv pipe
```

## Serve Alias

`nilo serve ...` は `nilo server ...` の compatibility alias です。

```bash
nilo serve run --host 127.0.0.1 --port 8000
```

新しい文書では `nilo server ...` を優先してください。

MCP client configuration fields は [MCP Clients](../MCP_Clients.md) を参照してください。
