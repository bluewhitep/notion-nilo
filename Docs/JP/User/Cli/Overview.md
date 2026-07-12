# CLI Overview

このページでは CLI 全体の共通動作を説明します。

## 共通ルール

- `-h` と `--help` は同じです。例: `nilo -h`、`nilo page -h`。
- 多くの read command は scripts や agents 向けに `--json` をサポートします。
- write、update、send、complete、trash など副作用のある command は、可能な場合 `--dry-run` で事前確認します。
- JSON input は `--payload`、`--properties`、`--arguments` で渡します。値は JSON object である必要があります。
- `page/pages`、`block/blocks`、`database/databases` などの複数形は alias です。ユーザー文書では通常単数形を使います。
- Git/gh と同様に、global commands はどの directory からでも動作し、project commands は user home まで上位探索して最も近い `.notion_mcp/` を使います。
- 実際の Notion call の前に `nilo config --global user.token <token>` で token を設定し、対象 content を Notion connection に共有してください。

## Short aliases

すべての public command には、6 文字以内の明示的な alphabetic short alias があります。文書では canonical name を primary form として使います。例:

```bash
nilo cfg --global --show
nilo pg get <page_id> --json
nilo srv start --host 127.0.0.1 --port 8000
```

主な root aliases は `init/ini`、`version/ver`、`config/cfg`、`pwd/cwd`、`page/pg`、`block/blk`、`database/db`、`data-source/ds`、`server/srv` です。

## Function Calling JSON errors

Function Calling では `--json` を付けます。unknown option、missing required parameter、invalid parameter の場合、CLI は Rich help の代わりに stable error code を含む exactly one compact JSON line を出力します。`--json` のない呼び出しでは human-readable help/error を維持します。

```json
{"ok":false,"error":{"type":"CliUsageError","code":"cli_missing_parameter","message":"...","details":{"exit_code":2}}}
```

## JSON input 例

```bash
nilo page update <page_id> --payload '{"properties": {}}'
nilo database query --payload '{"page_size": 10}'
nilo raw-api invoke search --arguments '{"query": "Tasks"}' --json
```

## 副作用の preview

```bash
nilo block append <block_id> --payload '{"children": []}' --dry-run --json
nilo block trash <block_id> --dry-run
```
