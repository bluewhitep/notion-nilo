# Installation

本文面向使用者，说明如何安装本地 Notion MCP 工具。

## 安装策略

推荐优先使用 `uv` 从本地路径安装。`uv tool install` 会把 `notion-mcp`
命令安装到持久 tool 环境，并把可执行入口暴露到 PATH。

如果本机没有安装 `uv`，可以使用 `pip` 从本地路径安装。

安装完成后，需要先完成 Notion 侧 connection、token、page/database 授权和 id 查询。详细步骤见 [Configuration](Configuration.md) 的 “Notion 侧准备”。

安装后的第一组命令通常是：

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global user.name "Ada"
notion-mcp config --global --show
```

新的配置命令统一使用 `notion-mcp config --global ...`。

## 使用 uv 安装

推荐安装方式：

```bash
cd /path/to/notion_mcp_project
uv tool install .
notion-mcp --help
```

如果安装后终端找不到 `notion-mcp`，先确认 uv tool executable directory 已经在 PATH 中：

```bash
uv tool update-shell
```

然后重新打开终端再运行：

```bash
notion-mcp --help
```

## 使用 uv 临时运行

不想持久安装时，可以从本地路径临时运行：

```bash
cd /path/to/notion_mcp_project
uv run --no-project --with . notion-mcp --help
```

## 无 uv 时使用 pip 安装

```bash
pip install /path/to/notion_mcp_project
notion-mcp --help
```

## 卸载

使用 `uv tool install` 安装时：

```bash
uv tool uninstall notion-mcp
```

使用 `pip install` 安装时：

```bash
pip uninstall notion-mcp
```

如果使用 `uv run --no-project --with .` 临时运行，不需要单独卸载。
