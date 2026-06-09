# Packaging

本文档面向开发者，说明本仓库的打包和本地安装策略。

## Package Layout

当前项目使用 `src` layout。

```text
src/
  notion_mcp/
```

console script：

```text
notion-mcp = notion_mcp.cli:app
```

构建后端：

```text
hatchling.build
```

选择 `hatchling` 的原因是隔离安装验证会从本地路径构建 wheel；该后端不会把 `build/`
或 `*.egg-info` 写回仓库工作树。

## Dependencies

核心依赖：

- `notion-client`
- `mcp`
- `typer`
- `pydantic`
- `fastapi`
- `uvicorn`

`fastapi` 当前只用于内部 REST 原型兼容代码。`uvicorn` 仍用于 HTTP server runtime。

## Runtime Stack

当前项目继续使用 Python，`pyproject.toml` 声明 `requires-python = ">=3.10"`。继续使用 Python 的原因是：

- 现有代码和测试都是 Python。
- Notion Python SDK 可复用。
- MCP Python SDK 可直接实现本地 MCP server。
- pytest、Typer、FastAPI 和 Pydantic 工具链已经存在。

Notion SDK 由 Core client factory 统一创建，并集中注入：

- bearer token
- Notion API version
- timeout
- retry policy
- fake client test double

CLI 和 MCP Tool 不应直接创建 Notion SDK client。

Notion API version 是全局配置项。当前默认目标版本为 `2026-03-11`，升级该版本时必须同步兼容性测试。

MCP Python SDK 用于创建真正的 MCP server、注册 tools、暴露 tool schema 并处理 stdio / Streamable HTTP transport。

Typer 是 CLI 框架；CLI 只调用 Core，支持普通文本输出、`--json` 输出和 `--dry-run`。

Pydantic 用于配置模型和结构化输入输出。当前代码使用 Pydantic v2 API。

开发验收依赖：

- `pytest`
- `pytest-asyncio`
- `httpx`
- `ruff`
- `mypy`

这些工具同时声明在 `dependency-groups.dev` 和 `project.optional-dependencies.dev`
中。前者支持仓库内 `uv run pytest`、`uv run ruff check .`、`uv run mypy src`
直接同步开发环境；后者保留 `notion-mcp[dev]` 形式的额外安装兼容性。

## Isolated Install

开发者验收命令：

```bash
uv run --no-project --with . notion-mcp --help
uv run --no-project --with . notion-mcp config --global --show --json
uv run --no-project --with . notion-mcp server run --help
```

## Release Checks

发布前验收命令：

```bash
uv run pytest -q -p no:cacheprovider
uv run ruff check .
uv run mypy src
```

`ruff` 和 `mypy` 的缓存目录配置到 `/tmp`，避免在仓库中留下 `.ruff_cache/`
或 `.mypy_cache/`。

## Generated Files

发布前必须清理：

- Python bytecode cache。
- build output。
- package egg-info。
- pytest cache。
- ruff cache。
- mypy cache。

这些文件不属于仓库源码。
