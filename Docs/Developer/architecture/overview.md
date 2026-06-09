# Architecture Overview

本文档面向开发者，说明当前仓库的架构边界。

## 当前目标

本仓库提供本地运行的 Notion MCP server。当前实现围绕以下三层展开：

- Core：唯一业务逻辑层。
- CLI：面向人类的 git-like 本地命令入口。
- MCP Tool：面向 Agent/LLM 的结构化工具入口。

使用者安装、Notion connection 配置和命令用法放在 `Docs/User/`；本目录只记录开发者需要维护的实现边界。

## 目标结构

```text
Human -> CLI -> Core
Agent / LLM -> MCP Tool -> Core
```

必须保持：

```text
CLI -> Core
MCP Tool -> Core
```

禁止：

```text
MCP Tool 通过 CLI 字符串绕行
CLI -> Notion SDK
MCP Tool -> Notion SDK
```

## Core

Core 是唯一业务逻辑层，负责：

- 全局配置读写、项目级上下文解析和 token 脱敏。
- 集中管理 Notion API version、timeout 和 retry。
- 统一创建 Notion SDK-compatible client。
- auth validate 和 user/bot 信息读取。
- 按对象域封装 Notion 服务：
  - pages
  - blocks
  - databases
  - data sources
  - users
  - comments
  - views
  - file uploads
  - search
  - custom emojis
- raw API 登记表和高级兜底调用。
- 本地审计和统一错误模型。

## CLI

CLI 是人类入口，负责：

- git-like 命令结构。
- 普通文本输出。
- `--json` 输出。
- `--dry-run`。
- 启动和管理 MCP server。

公开 server 命令包括：

```text
notion-mcp server run
notion-mcp server status
notion-mcp server stop
notion-mcp server logs
notion-mcp server remove
notion-mcp server stdio
```

CLI resource command 通过 Core service 调用 Notion 能力。

项目级 `.notion_mcp/` 目录只保存项目上下文和 attach state，不保存 token。全局配置继续保存 token、用户显示名和 Notion API version。

## MCP Tool

MCP Tool 是 Agent/LLM 入口，负责：

- tool inventory。
- input schema。
- tool annotations。
- 结构化错误。
- 危险操作确认。

MCP Tool 直接调用 Core service，不拼 CLI 字符串。

## 非功能边界

- token 默认不得在普通输出或 MCP config status 中明文泄露。
- CLI 和 MCP 写操作应支持 dry-run 或危险操作确认。
- live 测试默认跳过，只能在明确的测试 page/workspace 中运行。
- Notion-Version 由 Core 配置集中管理，不在 CLI、MCP tool 或单个服务里散落硬编码。
