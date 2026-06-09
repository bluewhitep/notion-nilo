# CLI API

本文档面向开发者，记录当前 `notion-mcp` CLI 的公开命令面、隐藏兼容入口和 Core 调用边界。CLI 负责终端使用体验，业务能力必须来自 Core service。

## 入口

- package：`notion_mcp.cli`
- console script：`notion-mcp = notion_mcp.cli:app`
- root app：`src/notion_mcp/cli/app.py`

## 核心边界

```text
CLI -> Core -> Notion SDK/API
MCP Tool -> Core -> Notion SDK/API
```

CLI 不应直接调用 Notion SDK。新增命令时，应先确认对应 Core service 能力；如果 Core 缺失，应先补 Core，再接 CLI。

## 公开 Root 命令

- `notion-mcp init`
  - 初始化当前目录的项目级 `.notion_mcp/`。
  - 不写入 token，不要求 user id。
- `notion-mcp pwd`
  - 从当前目录向上解析项目根目录。
- `notion-mcp version`
  - 输出 MCP package version 和配置的 Notion API version。
- `notion-mcp config --global --show`
  - 输出全局配置摘要，不暴露 token。
- `notion-mcp config --global user.token <token>`
  - 更新全局 token。
- `notion-mcp config --global user.name <name>`
  - 更新全局用户显示名称。
- `notion-mcp config --local --show`
  - 输出当前项目级配置摘要。

`project`、`local`、root `status`、`config global/local` 和 `config set/get/unset/list` 只保留为隐藏兼容入口，不属于公开命令面。

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

## Page CLI

公开命令：

Page id inputs are normalized through `src/notion_mcp/core/identifiers.py`. Public `<page_id>` arguments accept raw page ids, copied Notion URLs, and Markdown links that contain Notion URLs.

- `notion-mcp page attach <page_id>`
  - 绑定当前项目默认 page。
  - `attach` 语义是 project context binding，不是 file attachment。
- `notion-mcp page status`
  - 显示当前绑定 page。
- `notion-mcp page refresh`
  - 重新读取绑定 page 的标题、URL 和状态，只刷新本地 state，不修改 Notion 远端。
- `notion-mcp page detach`
  - 删除本地 page attach state，不修改 Notion 远端。
- `notion-mcp page retrieve [page_id]`
  - 读取 page 元信息。
  - 无参数时使用 attached page。
- `notion-mcp page blocks [page_id]`
  - 读取 page 内容块摘要。
  - 无参数时使用 attached page。
- `notion-mcp page create`
  - 创建 page。
  - payload 没有 parent 且存在 attached page 时，默认使用 attached page 作为 parent。
- `notion-mcp page create --parent-page <page_id>`
  - 在指定 parent page 下创建 child page。
- `notion-mcp page update <page_id>`
  - 更新普通 page 或 data source entry page properties。
- `notion-mcp page trash <page_id>`
  - 将 page 移入 trash。

隐藏兼容入口保留给旧的 page content/current/deattach aliases、旧 page-scoped block group 和旧 page insert group。它们不得作为公开用户命令记录。

## Block CLI

公开命令：

- `notion-mcp block children <block_id>`
  - 列出 child blocks。
- `notion-mcp block append <block_id>`
  - 追加 child blocks。
- `notion-mcp block insert-after <block_id>`
  - 在目标 block 后插入 sibling blocks。
- `notion-mcp block update <block_id>`
  - 更新 block。
- `notion-mcp block trash <block_id>`
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

- `notion-mcp database attach <database_id>`
- `notion-mcp database attach <database_id> --data-source <id_or_name>`
- `notion-mcp database status`
- `notion-mcp database refresh`
- `notion-mcp database detach`
- `notion-mcp database retrieve [database_id]`
- `notion-mcp database sources [database_id]`
- `notion-mcp database create`
- `notion-mcp database create --parent-page <page_id>`
- `notion-mcp database update <database_id>`
- `notion-mcp database rename <database_id> <new_name>`

`database create` 创建 database 容器，并创建 initial data source。`database update` 只允许容器级更新，不用于修改 data source schema。

### Database 快捷命令

这些命令只作用于 attached database 的 active data source：

- `notion-mcp database query --payload <json>`
- `notion-mcp database page create --properties <json>`
- `notion-mcp database property rename <property> <new_name>`

公开 CLI 不提供 `database query --data-source`、`database page create <data_source_id>`、`database page update <page_id>` 或三参数 `database property rename`。显式 data source 操作必须使用 `data-source`；page property 更新使用 `page update`。

### DataSource 命令

- `notion-mcp data-source retrieve <data_source_id>`
- `notion-mcp data-source query <data_source_id>`
- `notion-mcp data-source create`
- `notion-mcp data-source create <database_id>`
- `notion-mcp data-source update <data_source_id>`
- `notion-mcp data-source templates <data_source_id>`
- `notion-mcp data-source property rename <data_source_id> <property> <new_name>`
- `notion-mcp data-source page create <data_source_id>`

## 其他对象域

- `notion-mcp auth validate`
- `notion-mcp auth whoami`
- `notion-mcp user me/list/retrieve`
- `notion-mcp comment list/create/reply`
- `notion-mcp view retrieve/list/query/create/update`
- `notion-mcp file-upload retrieve/list/create/send/complete`
- `notion-mcp search query`
- `notion-mcp custom-emoji list/retrieve`
- `notion-mcp raw-api operations`
- `notion-mcp raw-api invoke <operation>`
- `notion-mcp server run`
- `notion-mcp server status`
- `notion-mcp server stop`
- `notion-mcp server logs`
- `notion-mcp server remove`
- `notion-mcp server stdio`

Raw API 是高级兜底入口，不应作为普通 page/database 编辑路径。

## 移除的旧入口

以下旧 root 命令不再作为公开 CLI 入口：

- `notion-mcp set-token`
- `notion-mcp set-user`
- `notion-mcp show`
- `notion-mcp run`
- `notion-mcp mcp serve`

配置使用 `notion-mcp config --global ...`；MCP server 使用 `notion-mcp server ...`。
