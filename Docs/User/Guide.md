# 使用指南

本文面向最终使用者，介绍如何安装并使用本地 Notion MCP 服务。通过本服务，可以在 AI 工具或脚本中调用 Notion API，实现页面、数据库、区块等对象域的读取和写入。

## 当前状态

当前可用入口包括 git-like CLI 和本地 MCP server。

CLI 使用说明见 [Cli](Cli.md)。
MCP client 使用说明见 [MCP Clients](MCP_Clients.md)。

## 前提条件

1. **创建 Notion 集成**：在使用本服务前，需要先在 Notion 中创建内部集成，并记录生成的集成 token。
2. **授予页面访问权限**：在 Notion 中将需要访问的页面或数据库连接到该集成。
3. **安装 Python 3.10+**：本项目基于 Python 开发，请确保系统已安装 Python 3.10 或更高版本。

## 安装

推荐使用 uv 从仓库根目录安装：

```bash
cd /path/to/notion_mcp_project
uv tool install .
notion-mcp --help
```

如果本机没有安装 `uv`，可以使用 `pip` 从本地路径安装。

更完整的安装说明见 [Installation](Installation.md)。

## 初始化配置

首次使用需设置全局 Notion token。普通用户不需要手动填写 `user_id`。

```bash
# 设置全局 token 和可选用户名
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global user.name Ada

# 查看保存的配置和 token 状态
notion-mcp config --global --show --json

# 查看当前 token 对应的 Notion identity
notion-mcp auth whoami --json
```

配置文件默认存储在 `~/.notion_mcp/config.json`。可以通过环境变量 `NOTION_MCP_CONFIG` 指定其他路径。

## 启动 MCP Server

如果 MCP client 使用命令型 stdio server，配置为：

```bash
notion-mcp server stdio
```

如果 MCP client 支持 streamable-http URL，可以后台启动本地 server：

```bash
notion-mcp server run --host 127.0.0.1 --port 8000
notion-mcp server status
```

MCP client 配置说明见 [MCP Clients](MCP_Clients.md)。

## 调用示例

CLI 示例：

```bash
notion-mcp page retrieve <page_id> --json
notion-mcp data-source query <data_source_id> --json
notion-mcp block children <block_id> --json
```

## 常见问题

### 1. 为什么提示“未设置 Notion token”？

这是因为在调用接口前还没有设置全局 token。请运行：

```bash
notion-mcp config --global user.token ntn_xxx
```

### 2. 是否需要填写 Notion 用户 UUID？

普通用户不需要手动填写。需要排查当前 token 身份时，运行 `notion-mcp auth whoami --json` 查看返回的 `user_id`。

### 3. 是否支持 OAuth 授权？

当前版本仅支持内部集成 token。OAuth 支持不在当前用户流程中。

### 4. 调用返回错误怎么办？

一般情况下，错误来自配置、权限或 Notion API 参数。请检查：

1. 是否已正确设置 token 且没有过期；
2. 是否已授权集成访问对应的页面或数据库；
3. 调用参数是否符合 Notion API 要求。

若确认上述问题均无误，可查看 CLI 输出、MCP client 日志或本地服务日志。

---

本指南介绍了从安装到使用本地 Notion MCP 服务的完整流程。
