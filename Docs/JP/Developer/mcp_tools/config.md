# Config Tools

- `config_status`
  - 説明: local configuration status、redacted configuration、capability flags を返します。
  - Required parameters: none.
  - Returns: `configured`, `config`, `capabilities`.
- `config_get`
  - 説明: non-secret configuration field を 1 つ読み取ります。
  - Required parameters: `key`.
  - Optional parameters: none.
  - Security: MCP は raw `notion_token` を返しません。設定済みの場合も常に `********` を返します。
