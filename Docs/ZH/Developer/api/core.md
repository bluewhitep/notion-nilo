# Core API

本文档面向开发者，记录 `src/nilo/core/` 当前已经实现的 Core 能力。Core 是唯一业务逻辑层，CLI 和 MCP Tool 都应调用 Core，而不是直接调用 Notion SDK。

## 配置

模块：`src/nilo/core/config.py`

- `CoreConfig`
  - 保存 `notion_token`、`user_name`、`user_id`、`notion_version`、`timeout_ms`、`retry`、`default_transport` 和 `audit_enabled`。
  - `user_id` 必须是 UUID。
  - 默认 `notion_version` 为 `2026-03-11`。
- `init_core_config(...)`
  - 初始化配置并写入本地配置文件。
  - 配置文件权限写为 `0600`。
- `load_global_core_config(...)`
  - 只读取全局配置，不应用项目级覆盖项。
- `load_core_config(...)`
  - 返回有效配置：以全局凭据和设置为基础，再应用最近项目中的非敏感设置覆盖项。
  - 项目只允许覆盖 `notion_version`、`timeout_ms`、`retry`、`default_transport` 和 `audit_enabled`。
- `resolve_config_locations(...)`
  - 按 Git-like 方式向上查找项目，并返回 `ConfigLocations(project_dir, global_dir)`。
  - 起始路径位于用户 home 树内时，查找在 home 之前停止；home 只算全局配置位置。
  - workspace 位于 home 树外（例如外接磁盘或挂载目录）时，查找继续向上到该文件系统根之前，但绝不把文件系统根本身作为项目。
  - 全局查找与项目查找相互独立，只使用用户 home 或 `NOTION_MCP_CONFIG`。项目配置或全局配置缺失时，各自独立返回 `None`。
- `update_core_config(...)`
  - 只更新传入字段，不清空未传入字段。
- `redacted_config(...)`
  - 返回状态输出使用的脱敏配置，不泄露 token。

全局配置默认是 `~/.notion_mcp/config.json`，也可以由 `NOTION_MCP_CONFIG` 指向其他文件。项目配置是有效查找边界以下最近的 `.notion_mcp/config.json`，也可以位于 home 树外的 workspace。项目设置优先于全局设置，但凭据只能保存在全局配置中。初始化项目时，如果项目根 `.gitignore` 不存在会创建该文件，并在保留原内容的前提下增量加入精确条目 `.notion_mcp/`。

## 错误模型

模块：`src/nilo/core/errors.py`

- `CoreError`
  - 所有 Core 错误的基类。
  - `to_dict()` 返回 `type`、`code`、`message`、`details`。
- `ConfigNotFoundError`
- `ConfigValidationError`
- `NotionAuthError`
- `NotionOperationError`

CLI JSON 输出和 MCP tool 响应应复用这些错误结构。

## Notion SDK Client

模块：`src/nilo/core/client.py`

- `NotionClientFactory`
  - 从 `CoreConfig` 创建 Notion SDK client。
  - 注入 `auth`、`notion_version`、`timeout_ms` 和 `retry`。
  - 支持 `client_cls` 和 `fake_client`，用于测试和后续 MCP 场景测试。
- `create_notion_client(...)`
  - 默认 client factory 入口。

## 认证

模块：`src/nilo/core/auth.py`

- `AuthService.validate(...)`
  - 调用 `client.users.me()` 校验 token。
  - 可传入 `expected_user_id`，用于校验配置中的 Notion 用户 UUID 是否匹配当前 token。
  - 返回 `AuthValidationResult`。

## 审计

模块：`src/nilo/core/audit.py`

- `AuditRecorder.record(...)`
  - 写入 JSONL 审计记录。
  - 字段包含 `timestamp`、`configured_user_id`、`operation`、`target`、`dry_run` 和 `metadata`。
  - 会移除 `notion_token`、`token`、`auth`、`authorization`、`bearer` 等敏感字段。

## Notion 对象域服务

目录：`src/nilo/core/services/`

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

模块 `src/nilo/core/services/provider.py` 是 client 与对象域 service 的通用组合入口。CLI、MCP 和兼容适配层都导入这些 Core provider，不各自维护重复 factory。

## 通用 Runtime API

目录：`src/nilo/runtime/`

Runtime 保存适配层共用的非业务执行能力：

- 受管后台 Streamable HTTP server 的进程状态、状态查询、日志、停止和移除；
- 前台 stdio server 进程启动；
- server command、runtime path 和生命周期 helper。

Runtime 可以依赖 Core 契约。Core/Runtime 不导入 CLI 或 MCP 适配层，CLI 也不导入 MCP。

## Raw API

模块：`src/nilo/core/services/raw_api.py`

- `registered_operations()`
  - 返回允许 pass-through 的 Notion SDK 操作名。
- `RawNotionService.invoke(operation, arguments)`
  - 只允许调用登记表内的操作。
  - 禁止未登记操作和私有属性。
  - 用于补足 “支持 Notion SDK/API 公开能力” 的扩展入口。
