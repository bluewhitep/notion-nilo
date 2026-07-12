# Config Tools

- `config_status`
  - 说明：返回本地配置状态、脱敏配置和能力标记。
  - 必选参数：无。
  - 返回：`configured`、`config`、`capabilities`。
- `config_get`
  - 说明：读取一个非敏感配置字段。
  - 必选参数：`key`。
  - 可选参数：无。
  - 安全：MCP 永远不会返回原始 `notion_token`；已配置时该字段始终返回 `********`。
