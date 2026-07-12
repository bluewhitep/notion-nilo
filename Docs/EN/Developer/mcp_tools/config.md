# Config Tools

- `config_status`
  - Description: returns local configuration status, redacted configuration, and capability flags.
  - Required parameters: none.
  - Returns: `configured`, `config`, and `capabilities`.
- `config_get`
  - Description: reads one non-secret configuration field.
  - Required parameters: `key`.
  - Optional parameters: none.
  - Security: MCP never returns the raw `notion_token`; the field always returns `********` when configured.
