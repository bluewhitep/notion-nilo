# CLI API

本文档面向开发者，记录当前 `nilo` CLI 的公开命令面、隐藏兼容入口和 Core 调用边界。CLI 负责终端使用体验，业务能力必须来自 Core service。

## 入口

- package：`nilo.cli`
- console script：`nilo = nilo.cli:app`
- root app：`src/nilo/cli/app.py`
- help options：`--help` and `-h`

## 核心边界

```text
CLI -> Core 或 Runtime
MCP -> Core 或 Runtime
```

CLI 不得直接调用 Notion SDK，也不得导入 MCP 适配层。通用业务能力属于 Core，通用进程/执行能力属于 Runtime；Core/Runtime 不得反向导入 CLI 或 MCP。新增命令时应先确认对应通用能力已经存在；CLI 模块只定义 CLI 特有的参数解析、展示和交互。

## 公开 Root 命令

- `nilo init`
  - 初始化当前目录的项目级 `.notion_mcp/`。
  - 不写入 token，不要求 user id。
- `nilo pwd`
  - 从当前目录向上解析项目根目录。
- `nilo version`
  - 输出 MCP package version 和配置的 Notion API version。
- `nilo config --global --show`
  - 输出全局配置摘要，不暴露 token。
- `nilo config --global user.token <token>`
  - 更新全局 token。
- `nilo config --global user.name <name>`
  - 更新全局用户显示名称。
- `nilo config --local --show`
  - 输出当前项目级配置摘要。

`project`、`local`、root `status`、`config global/local` 和 `config set/get/unset/list` 只保留为隐藏兼容入口，不属于公开命令面。

CLI 使用类似 Git/gh 的作用域：全局命令可以在任意目录运行；项目级命令从当前目录向上查找最近的 `.notion_mcp/`，最多查到用户根目录。

## 短别名契约

每个公开规范命令路径都有一个显式英文字母别名，长度不超过六个字符。规范全称仍是文档主接口；短别名调用相同 callback，并在普通 help 中隐藏以保持帮助简洁。

Root 示例：

| 全称 | 别名 |
| --- | --- |
| `init` | `ini` |
| `version` | `ver` |
| `config` | `cfg` |
| `pwd` | `cwd` |
| `page` | `pg` |
| `block` | `blk` |
| `database` | `db` |
| `data-source` | `ds` |
| `server` | `srv` |

Leaf 示例包括 `retrieve -> get`、`create -> new`、`update -> upd`、`trash -> del` 和 `server run -> server start`。完整且经过校验的映射定义在 `src/nilo/cli/aliases.py`。

## Function Calling 错误契约

只要调用参数中任意位置出现 `--json`，Click/Typer 用法错误就输出为一行紧凑 JSON。稳定 envelope 包含 `ok=false`，以及带有 `type`、`code`、`message`、`details.exit_code` 的 `error` object。稳定用法错误码包括 `cli_missing_parameter`、`cli_invalid_parameter`、`cli_unknown_option` 和 `cli_usage_error`。不带 `--json` 的人类调用继续使用普通 help 和错误格式。

## Project Context

项目上下文由 Core 提供：

```text
ProjectResolver
ProjectConfigStore
AttachmentStore
ContextResolver
```

解析规则：

```text
explicit id > attached state > error
```

项目级配置：

```text
.notion_mcp/config.json
```

Attach state：

```text
.notion_mcp/state/page.attach.json
.notion_mcp/state/database.attach.json
```

项目级配置和 attach state 不得保存 token。

项目级配置只能覆盖非敏感 Core 设置，全局凭据始终保存在全局配置中。项目初始化拒绝把用户根目录作为项目根，并在项目根 `.gitignore` 中增量加入 `.notion_mcp/`。

## Page CLI

公开命令：

Page id inputs are normalized through `src/nilo/core/identifiers.py`. Public `<page_id>` arguments accept raw page ids, copied Notion URLs, and Markdown links that contain Notion URLs.

- `nilo page attach <page_id>`
  - 绑定当前项目默认 page。
  - `attach` 语义是 project context binding，不是 file attachment。
- `nilo page status`
  - 显示当前绑定 page。
- `nilo page refresh`
  - 重新读取绑定 page 的标题、URL 和状态，只刷新本地 state，不修改 Notion 远端。
- `nilo page detach`
  - 删除本地 page attach state，不修改 Notion 远端。
- `nilo page retrieve [page_id]`
  - 读取 page 元信息。
  - 无参数时使用 attached page。
- `nilo page blocks [page_id]`
  - 读取 page 内容块摘要。
  - 无参数时使用 attached page。
- `nilo page create`
  - 创建 page。
  - payload 没有 parent 且存在 attached page 时，默认使用 attached page 作为 parent。
- `nilo page create --parent-page <page_id>`
  - 在指定 parent page 下创建 child page。
- `nilo page update <page_id>`
  - 更新普通 page 或 data source entry page properties。
- `nilo page trash <page_id>`
  - 将 page 移入 trash。

隐藏兼容入口保留给旧的 page content/current/deattach aliases、旧 page-scoped block group 和旧 page insert group。它们不得作为公开用户命令记录。

## Block CLI

公开命令：

- `nilo block children <block_id>`
  - 列出 child blocks。
- `nilo block append <block_id>`
  - 追加 child blocks。
- `nilo block insert-after <block_id>`
  - 在目标 block 后插入 sibling blocks。
- `nilo block update <block_id>`
  - 更新 block。
- `nilo block trash <block_id>`
  - 将 block 移入 trash。

`insert-before` 不作为稳定公开命令。`block remove` 只作为隐藏兼容别名，行为等同 trash。

## Database 和 DataSource

语义边界：

```text
database = container
data_source = table under database
page = page or data source entry
block = page content node
```

容器级能力使用 `database`。表级 schema/query/templates/page-entry 能力使用 `data-source`。只有使用当前绑定 database 的 active data source 时，才允许 `database` 快捷命令。

### Database 容器命令

- `nilo database attach <database_id>`
- `nilo database attach <database_id> --data-source <id_or_name>`
- `nilo database status`
- `nilo database refresh`
- `nilo database detach`
- `nilo database retrieve [database_id]`
- `nilo database sources [database_id]`
- `nilo database create`
- `nilo database create --parent-page <page_id>`
- `nilo database update <database_id>`
- `nilo database rename <database_id> <new_name>`

`database create` 创建 database 容器，并创建 initial data source。`database update` 只允许容器级更新，不用于修改 data source schema。

### Database 快捷命令

这些命令只作用于 attached database 的 active data source：

- `nilo database query --payload <json>`
- `nilo database page create --properties <json>`
- `nilo database property rename <property> <new_name>`

公开 CLI 不提供 `database query --data-source`、`database page create <data_source_id>`、`database page update <page_id>` 或三参数 `database property rename`。显式 data source 操作必须使用 `data-source`；page property 更新使用 `page update`。

### DataSource 命令

- `nilo data-source retrieve <data_source_id>`
- `nilo data-source query <data_source_id>`
- `nilo data-source create`
- `nilo data-source create <database_id>`
- `nilo data-source update <data_source_id>`
- `nilo data-source templates <data_source_id>`
- `nilo data-source property rename <data_source_id> <property> <new_name>`
- `nilo data-source page create <data_source_id>`

## 其他对象域

- `nilo auth validate`
- `nilo auth whoami`
- `nilo user me/list/retrieve`
- `nilo comment list/create/reply`
- `nilo view retrieve/list/query/create/update`
- `nilo file-upload retrieve/list/create/send/complete`
- `nilo search query`
- `nilo custom-emoji list/retrieve`
- `nilo raw-api operations`
- `nilo raw-api invoke <operation>`
- `nilo server run`
- `nilo server status`
- `nilo server stop`
- `nilo server logs`
- `nilo server remove`
- `nilo server stdio`

Raw API 是高级兜底入口，不应作为普通 page/database 编辑路径。

## 移除的旧入口

以下旧 root 命令不再作为公开 CLI 入口：

- `nilo set-token`
- `nilo set-user`
- `nilo show`
- `nilo run`
- `nilo mcp serve`

配置使用 `nilo config --global ...`；MCP server 使用 `nilo server ...`。
