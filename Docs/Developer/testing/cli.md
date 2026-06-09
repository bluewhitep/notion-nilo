# CLI 测试文档

本文档面向开发者，说明 CLI 测试覆盖目标和常用验证方式。详细历史记录保存在开发进度资料中。

## 覆盖目标

- Root command：验证 `init`、`pwd`、`version`、server lifecycle commands 和帮助文本。
- Config commands：验证 `config --global` 管理全局配置，`config --local --show` 读取项目级配置，token 默认脱敏。
- Project context：验证项目级 `.notion_mcp/` 初始化、状态读取、root 解析和隐藏兼容入口。
- Page commands：验证 page attach/status/refresh/detach/retrieve/blocks/create/update，以及 hidden compatibility aliases。
- Block commands：验证 block append/insert-after/update/trash 和底层 children 读取。
- Database/DataSource commands：验证 database 容器命令、data-source 表级命令、database 快捷命令和 attached active data source 默认解析。
- Raw API：验证 registered operation 仍可调用，并且 Raw API 只作为高级兜底入口。
- Output contract：验证 CLI prompt/output、HTTP error detail 和 schema description 使用英文；`--json` 输出结构保持稳定。
- Boundary contract：验证 CLI 命令调用 Core service，不直接导入 Notion SDK。

## 常用验证命令

Focused CLI 验证：

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_cli_docs uv run pytest -q -p no:cacheprovider
```

文档清单和用户文档边界验证：

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_docs uv run pytest -q -p no:cacheprovider
```

隔离安装验收：

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_install uv run --no-project --with . notion-mcp --help
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_install uv run --no-project --with . notion-mcp config --global --show --json
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/notion_mcp_uv_install uv run --no-project --with . notion-mcp server run --help
```

## 备注

- 真实 Notion workspace 验证必须显式启用，并使用安全的测试 page/database。
- 如果新增 CLI 行为影响用户手册，必须同步更新 `Docs/User/Cli.md`。
- 如果新增命令涉及配置、token、attach state 或 Notion permission，必须同步更新 `Docs/User/Configuration.md`。
