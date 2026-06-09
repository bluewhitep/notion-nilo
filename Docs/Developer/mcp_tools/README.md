# MCP Tools 开发者文档

本文档是 MCP tool 文档入口。当前仓库已实现 `src/notion_mcp/mcp_server/`，使用 MCP Python SDK 的 `FastMCP` 暴露本地工具。

## Server

- server factory：`src/notion_mcp/mcp_server/server.py`
- package entry：`notion_mcp.mcp_server:create_mcp_server`
- CLI stdio entry：`notion-mcp server stdio`
- CLI background HTTP entry：`notion-mcp server run --host 127.0.0.1 --port 8000`
- 支持 transport：`stdio`、`streamable-http`

## 工具域文档

- `config.md`
- `auth.md`
- `pages.md`
- `blocks.md`
- `databases.md`
- `data_sources.md`
- `users.md`
- `comments.md`
- `views.md`
- `file_uploads.md`
- `search.md`
- `custom_emojis.md`
- `raw_api.md`

## Tool Inventory

当前 server 可枚举 46 个 tools：

- `auth_validate`
- `auth_whoami`
- `block_append`
- `block_children_list`
- `block_trash`
- `block_update`
- `comment_create`
- `comment_list`
- `comment_reply`
- `config_get`
- `config_status`
- `custom_emoji_list`
- `custom_emoji_retrieve`
- `data_source_create`
- `data_source_property_rename`
- `data_source_query`
- `data_source_retrieve`
- `data_source_templates`
- `data_source_update`
- `database_create`
- `database_query`
- `database_rename`
- `database_retrieve`
- `database_sources`
- `database_update`
- `file_upload_complete`
- `file_upload_create`
- `file_upload_list`
- `file_upload_retrieve`
- `file_upload_send`
- `page_create`
- `page_property_retrieve`
- `page_retrieve`
- `page_trash`
- `page_update`
- `raw_api_invoke`
- `raw_api_registered_operations`
- `search`
- `user_list`
- `user_me`
- `user_retrieve`
- `view_create`
- `view_list`
- `view_query`
- `view_retrieve`
- `view_update`

## 公共规则

- MCP Tool 只能调用 Core，不能调用 CLI。
- 工具错误应返回结构化 `{"ok": false, "error": ...}`。
- token 默认必须脱敏。
- 删除、归档、trash 类危险工具必须带 `destructiveHint`，并要求 `confirm=true`。
- live Notion 权限、付费计划或真实 workspace 才能验证的能力，必须在测试和进度文档中标记。
