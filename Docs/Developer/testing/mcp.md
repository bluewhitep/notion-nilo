# MCP 测试文档

本文档面向开发者，说明 MCP server 和 MCP tools 的测试覆盖目标。详细历史记录保存在开发进度资料中。

## 覆盖目标

- Server lifecycle：验证 MCP server 可创建、可启动，并暴露预期 server 名称。
- Tool inventory：验证 tools 覆盖 config、auth、pages、blocks、databases、data_sources、users、comments、views、file_uploads、search、custom_emojis 和 raw_api。
- Tool schema：验证每个 tool 有 description、input schema 和结构化输出。
- Tool calls：验证 MCP tool 调用 Core service，不调用 CLI，也不直接创建 Notion SDK client。
- Dangerous tools：验证 trash/delete 等危险操作带有提示，并支持 confirmation guard。
- Client flow：验证 MCP client 风格的 list tools 和 call tool 流程。

## 常用验证命令

MCP focused 验证：

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_mcp uv run pytest -q -p no:cacheprovider
```

隔离安装 MCP help 验证：

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_mcp_install uv run --no-project --with . notion-mcp server run --help
```

## 备注

- MCP Tool 和 CLI 共享 Core，不共享命令字符串。
- Raw API tool 是高级兜底入口，不应成为普通 page/database workflow 的默认路径。
- 真实 Notion live 验证必须显式配置 token 和安全测试资源。
