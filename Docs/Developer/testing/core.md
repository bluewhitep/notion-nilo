# Core 测试文档

本文档面向开发者，说明 Core 层测试覆盖目标和常用验证方式。详细历史记录保存在开发进度资料中。

## 覆盖目标

- 配置模型：验证初始化、读取、更新、路径覆盖、文件权限、token 脱敏、UUID 校验和默认 Notion API version。
- 错误模型：验证 Core error code、message、details 和 CLI/MCP 可消费结构。
- Client factory：验证 Notion SDK client 初始化时注入 token、version、timeout、retry，并支持 fake client。
- Auth：验证 `users.me()` token 校验、configured user id 匹配和错误包装。
- Services：验证 pages、blocks、databases、data sources、users、comments、views、file uploads、search、custom emojis 和 raw API service 行为。
- Audit：验证 JSONL 审计记录和敏感字段清理。
- Boundary：验证 Core 不依赖 CLI、MCP server 或内部 REST 原型 routes。

## 常用验证命令

Core focused 验证：

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_core uv run pytest -q -p no:cacheprovider
```

全量本地验证：

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_full uv run pytest -q -p no:cacheprovider
```

## 备注

- Core 是 CLI 和 MCP Tool 的共同业务层。
- 新增 Notion API 能力时，应优先在 Core 层补齐测试，再同步 CLI/MCP 入口。
- 真实 Notion live 测试默认跳过，不能伪造通过。
