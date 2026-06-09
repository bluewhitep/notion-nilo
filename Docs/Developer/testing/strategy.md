# Testing Strategy

本文档面向开发者，说明测试分层和执行策略。

## 分层

- compatibility tests
  - 保持公开 CLI 和 MCP Tool 行为可回归。
  - 不为了新实现修改旧测试。
- Core tests
  - 覆盖配置、错误、client factory、auth、services、raw API、审计。
- CLI tests
  - 覆盖 init、config、status、resource command、dry-run。
- MCP tests
  - 覆盖 server lifecycle、tool inventory、tool calls、dangerous tools。
- Scenario tests
  - 覆盖本地配置流程、CLI 到 Core 到 fake Notion、MCP 到 Core 到 fake Notion、隔离安装。
- live tests
  - 默认跳过。
  - 只在显式环境变量启用时访问真实 Notion。

## 测试规则

- 新功能先写测试，再写实现。
- 已有测试一旦创建，不能为了通过而修改。
- 覆盖不足时新增更明确的测试文件，并在进度文档记录原因。
- live 测试不得伪造通过。

## 常用命令

```bash
uv run pytest -q -p no:cacheprovider
uv run pytest -q tests/live
```

如果需要隔离安装验证：

```bash
uv run --no-project --with . notion-mcp --help
uv run --no-project --with . notion-mcp server run --help
```
