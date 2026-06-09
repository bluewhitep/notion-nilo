# Core API

本文档面向开发者，记录 `src/notion_mcp/core/` 当前已经实现的 Core 能力。Core 是唯一业务逻辑层，CLI 和 MCP Tool 都应调用 Core，而不是直接调用 Notion SDK。

## 配置

模块：`src/notion_mcp/core/config.py`

- `CoreConfig`
  - 保存 `notion_token`、`user_name`、`user_id`、`notion_version`、`timeout_ms`、`retry`、`default_transport` 和 `audit_enabled`。
  - `user_id` 必须是 UUID。
  - 默认 `notion_version` 为 `2026-03-11`。
- `init_core_config(...)`
  - 初始化配置并写入本地配置文件。
  - 配置文件权限写为 `0600`。
- `load_core_config(...)`
  - 读取配置文件并返回严格校验后的 `CoreConfig`。
- `update_core_config(...)`
  - 只更新传入字段，不清空未传入字段。
- `redacted_config(...)`
  - 返回状态输出使用的脱敏配置，不泄露 token。

## 错误模型

模块：`src/notion_mcp/core/errors.py`

- `CoreError`
  - 所有 Core 错误的基类。
  - `to_dict()` 返回 `type`、`code`、`message`、`details`。
- `ConfigNotFoundError`
- `ConfigValidationError`
- `NotionAuthError`
- `NotionOperationError`

CLI JSON 输出和 MCP tool 响应应复用这些错误结构。

## Notion SDK Client

模块：`src/notion_mcp/core/client.py`

- `NotionClientFactory`
  - 从 `CoreConfig` 创建 Notion SDK client。
  - 注入 `auth`、`notion_version`、`timeout_ms` 和 `retry`。
  - 支持 `client_cls` 和 `fake_client`，用于测试和后续 MCP 场景测试。
- `create_notion_client(...)`
  - 默认 client factory 入口。

## 认证

模块：`src/notion_mcp/core/auth.py`

- `AuthService.validate(...)`
  - 调用 `client.users.me()` 校验 token。
  - 可传入 `expected_user_id`，用于校验配置中的 Notion 用户 UUID 是否匹配当前 token。
  - 返回 `AuthValidationResult`。

## 审计

模块：`src/notion_mcp/core/audit.py`

- `AuditRecorder.record(...)`
  - 写入 JSONL 审计记录。
  - 字段包含 `timestamp`、`configured_user_id`、`operation`、`target`、`dry_run` 和 `metadata`。
  - 会移除 `notion_token`、`token`、`auth`、`authorization`、`bearer` 等敏感字段。

## Notion 对象域服务

目录：`src/notion_mcp/core/services/`

当前已按对象域建立服务模块：

- `blocks.py`
- `pages.py`
- `databases.py`
- `data_sources.py`
- `users.py`
- `comments.py`
- `views.py`
- `file_uploads.py`
- `search.py`
- `custom_emojis.py`
- `raw_api.py`

这些服务只依赖 Core 和 Notion SDK-compatible client，不导入 CLI 或 MCP 层。

## Raw API

模块：`src/notion_mcp/core/services/raw_api.py`

- `registered_operations()`
  - 返回允许 pass-through 的 Notion SDK 操作名。
- `RawNotionService.invoke(operation, arguments)`
  - 只允许调用登记表内的操作。
  - 禁止未登记操作和私有属性。
  - 用于补足 “支持 Notion SDK/API 公开能力” 的扩展入口。
