# Architecture Overview

本文档面向开发者，说明当前仓库的架构边界。

## 当前目标

N.I.L.O. 提供本地运行的 MCP server。当前实现由两个通用实现层和两个薄适配层组成：

- Core：唯一业务逻辑层。
- Runtime：不属于业务逻辑的通用进程与执行生命周期层。
- CLI：面向人类的 git-like 本地命令入口。
- MCP server/tools：面向 Agent/LLM 的结构化适配层。

使用者安装、Notion connection 配置和命令用法放在 `Docs/ZH/User/`；本目录只记录开发者需要维护的实现边界。

## 目标结构

```text
Human / Function Calling -> CLI adapter -> Core / Runtime
Agent / LLM -> MCP adapter -> Core / Runtime
```

必须保持：

```text
CLI -> Core
CLI -> Runtime
MCP Tool -> Core
MCP Tool -> Runtime
```

禁止：

```text
CLI -> MCP
MCP -> CLI
Core 或 Runtime -> CLI 或 MCP
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

Core 也负责组合全局与项目级配置。有效配置先加载全局凭据，再应用用户根目录以下最近项目中的非敏感覆盖项。项目设置优先于全局设置；token 等凭据只能保存在全局配置中。

## Runtime

Runtime 保存通用的非业务执行能力，包括受管 server 进程状态、日志路径、后台 Streamable HTTP 生命周期和前台 stdio 进程启动。CLI 与 MCP 适配层可以导入 Runtime；Runtime 不得反向导入任何适配层。

## CLI

CLI 是人类入口，负责：

- git-like 命令结构。
- 普通文本输出。
- `--json` 输出，包括面向 Function Calling 的单行稳定用法错误 envelope。
- 为所有公开命令提供不超过六个字母的显式短别名。
- `--dry-run`。
- 启动和管理 MCP server。

公开 server 命令包括：

```text
nilo server run
nilo server status
nilo server stop
nilo server logs
nilo server remove
nilo server stdio
```

CLI resource command 通过 Core service 调用 Notion 能力，通过 Runtime 管理进程生命周期。CLI 不得导入 MCP 适配层。

项目级 `.notion_mcp/` 目录保存项目上下文、attach state 和非敏感设置覆盖项，不保存 token。全局配置保存凭据。项目定位只向上查到用户根目录；用户根目录下的 `.notion_mcp/` 只视为全局配置。项目初始化会在项目根 `.gitignore` 中增量加入 `.notion_mcp/`。

## MCP Tool

MCP Tool 是 Agent/LLM 入口，负责：

- tool inventory。
- input schema。
- tool annotations。
- 结构化错误。
- 危险操作确认。

MCP Tool 直接调用 Core service，不拼 CLI 字符串。

支持的 transport 只有两种：本地命令型 client 使用 `stdio`，URL 型服务/client 连接使用 `streamable-http`。不支持 legacy SSE。远程部署、认证、TLS 和反向代理配置本轮延期；当前 server 示例仅用于本地。

## 非功能边界

- token 默认不得在普通输出或 MCP config status 中明文泄露。
- CLI 和 MCP 写操作应支持 dry-run 或危险操作确认。
- live 测试默认跳过，只能在明确的测试 page/workspace 中运行。
- Notion-Version 由 Core 配置集中管理，不在 CLI、MCP tool 或单个服务里散落硬编码。
- 通用能力必须放在 Core 或 Runtime；CLI/MCP 模块只能定义各自适配层独有的功能。
