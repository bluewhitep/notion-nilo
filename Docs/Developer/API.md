# 开发者接口索引

本文档面向开发者，说明当前仓库的接口文档入口。当前项目已经从 REST 原型补全为本地 Notion MCP 服务器。

## 当前接口状态

- `src/notion_mcp/core/`：唯一业务逻辑层，供 CLI、MCP Tool 和兼容代码复用。
- `src/notion_mcp/server.py` 与 `src/notion_mcp/routes/`：内部 REST 原型兼容代码，不是公开 server CLI 入口，也不是最终 MCP Tool 接口。
- `src/notion_mcp/cli/`：git-like CLI，人类入口，调用 Core。
- `src/notion_mcp/mcp_server/`：MCP server 和 MCP tools，Agent/LLM 结构化入口，调用 Core。

## 文档入口

- Core API：`Docs/Developer/api/core.md`
- CLI API：`Docs/Developer/api/cli.md`
- Core 测试：`Docs/Developer/testing/core.md`
- CLI 测试：`Docs/Developer/testing/cli.md`
- MCP 测试：`Docs/Developer/testing/mcp.md`
- Live 测试：`Docs/Developer/testing/live.md`
- 场景测试：`Docs/Developer/testing/scenarios.md`
- MCP Tool contract：`Docs/Developer/mcp_tools/README.md`

## 调用边界

目标调用关系必须保持为：

```text
Human -> CLI -> Core
Agent / LLM -> MCP Tool -> Core
```

禁止 MCP Tool 通过 CLI 字符串调用，也禁止 CLI 和 MCP Tool 各自复制业务逻辑。
