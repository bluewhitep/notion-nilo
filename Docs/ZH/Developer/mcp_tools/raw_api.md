# Raw API Tools

- `raw_api_invoke`
  - 说明：调用 Core 登记表允许的 Notion SDK/API 操作。
  - 必选参数：`operation`。
  - 可选参数：`arguments`、`confirm`（默认 `false`）。
  - 安全：只允许 `src/nilo/core/services/raw_api.py` 中登记的操作，不允许任意属性穿透。`blocks.delete` 以及带 `archived=true` 或 `in_trash=true` 的 raw 调用必须先提供 `confirm=true`，才会进入 Core。
- `raw_api_registered_operations`
  - 说明：列出可调用的 raw API operation。
  - 必选参数：无。
