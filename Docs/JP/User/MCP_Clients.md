# MCP Clients

この文書では、MCP 対応ツールをローカル N.I.L.O. MCP server に接続する方法を説明します。

## 先に Notion token を設定する

MCP クライアントに Notion token を直接保存する必要はありません。token はローカルのグローバル設定に保存します。

```bash
nilo config --global user.token ntn_xxx
nilo config --global user.name "Ada"
nilo config --global --show
```

MCP クライアントはローカルの `nilo` server に接続するだけです。

## Transport を選ぶ

N.I.L.O. がサポートする transport は次の 2 つだけです。

| Transport | 向いている用途 | 事前に server 起動が必要か |
| --- | --- | --- |
| stdio | command/args で server を起動する local client | 不要 |
| streamable-http | MCP service URL に接続する local/remote client | 必要。service を先に起動 |

local command-launched client には stdio を使います。N.I.L.O. を service として実行し、client が URL で接続する場合は Streamable HTTP を使います。client は local/remote のどちらでも構いません。legacy SSE はサポートせず、transport value `sse` は拒否されます。

## Stdio 設定

stdio mode では、MCP クライアントが server process を起動・停止します。

設定値:

| Field | Value |
| --- | --- |
| Server name | `nilo` |
| Transport | `stdio` |
| Command | `nilo` |
| Arguments | `server`, `stdio` |

一般的な JSON:

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

1 行の command が必要なクライアントでは次を使います。

```text
nilo server stdio
```

`uv tool install .` でインストールした場合は、shell で次が実行できることを確認します。

```bash
nilo --help
```

クライアントが `nilo` を見つけられない場合:

```bash
uv tool update-shell
```

その後、ターミナルまたは MCP クライアントを再起動します。

## nilo をインストールしない Stdio 設定

`nilo` が `PATH` にない場合でも、MCP クライアントから `uv` 経由で repository path の `nilo` を実行できます。

| Field | Value |
| --- | --- |
| Server name | `nilo` |
| Transport | `stdio` |
| Command | `uv` |
| Arguments | `run`, `--no-project`, `--with`, `/path/to/notion-nilo`, `nilo`, `server`, `stdio` |

JSON 例:

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

`/path/to/notion-nilo` は自分の repository root に置き換えてください。

## Streamable HTTP 設定

MCP URL または streamable HTTP transport をサポートするクライアントでは、先にローカル server を起動します。

```bash
nilo server run --host 127.0.0.1 --port 8000
```

状態確認:

```bash
nilo server status
```

クライアント設定:

| Field | Value |
| --- | --- |
| Server name | `nilo` |
| Transport | `streamable-http` |
| URL | `http://127.0.0.1:8000/mcp` |
| Authentication | None（localhost example のみ） |

JSON 例:

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

クライアントが `http`、`streamableHttp`、`remote server` などの名前を使う場合は、URL を入力できる選択肢を選び、次を入力します。

```text
http://127.0.0.1:8000/mcp
```

MCP クライアントに Notion token を書かないでください。ローカル `nilo` server がローカル設定から読み取ります。

## Remote service scope

N.I.L.O. を将来 remote service として deploy する場合も、transport contract は `/mcp` endpoint の Streamable HTTP です。remote client は legacy SSE を選択してはいけません。この release で文書化・検証するのは上記 localhost server だけです。remote deployment、authentication、TLS、reverse proxy configuration は今回延期しているため、この unauthenticated localhost example を network に公開しないでください。

## Background server 管理

状態確認:

```bash
nilo server status
```

ログ:

```bash
nilo server logs --tail 100
```

停止:

```bash
nilo server stop
```

ローカル server state とログの削除:

```bash
nilo server remove
```

実行中プロセスも含めて強制 cleanup:

```bash
nilo server remove --force
```

これはローカル server runtime state だけを削除します。MCP client entry、コマンド、token 設定、project context の削除は [Uninstallation](Uninstallation.md) を参照してください。

## 環境変数

カスタムのグローバル設定ファイルを使う場合は、同じ環境変数を MCP クライアントにも渡します。

```text
NOTION_MCP_CONFIG=/path/to/config.json
```

stdio JSON 例:

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

## 現在の MCP Tool

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

クライアントに N.I.L.O. MCP tools が表示されない場合:

1. ターミナルで `nilo --help` を実行し、コマンドが存在するか確認します。
2. stdio では `command` と `args` が別フィールドか確認します。
3. streamable HTTP では `nilo server status` が running を示すか確認します。
4. `nilo server logs --tail 100` でログを確認します。
5. `nilo config --global --show` で Notion token が設定済みか確認します。

## Security notes

- token はローカル設定ファイルに保存されます。
- 通常の status 出力では token はマスクされます。
- MCP client 設定に Notion token は不要です。
- `Authentication: None` example は `127.0.0.1` のみ対象で、この release は remote deployment security を定義しません。
- `page_trash` や `block_trash` のような破壊的 tool は `confirm=true` を要求します。
- 実際の Notion 呼び出しには、connection が対象 page、database、workspace content に共有されている必要があります。
