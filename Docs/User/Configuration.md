# Configuration

本文面向使用者，说明如何准备 Notion connection、设置全局 token，以及如何在当前仓库中创建项目级 `.notion_mcp` 上下文。

## Notion 侧准备

在配置 `notion-mcp` 之前，先在 Notion 中创建一个 internal connection，并把它授权到要操作的 page 或 database。

1. 创建 Notion internal connection。
   - 打开 Notion Developer portal。
   - 在 Build / Internal connections 中创建新的 connection。
   - 填写 `Connection name`，例如 `notion-mcp-local`。这个名称会出现在 Notion 页面右上角 Connections / Add connection 的列表中。
   - `Authentication method` 选择 `Access token`。这个项目使用 Notion bearer token，不使用 `OAuth`。
   - 选择要使用的 workspace。
   - 在 Configuration 页复制 Installation access token。
   - token 通常以 `ntn_` 或 `secret_` 开头，后续写入全局配置。

2. 配置 connection capabilities。
   - Content capabilities：
     - `Read content`：查看已有 pages 和 database entries。读取 page、block、database 和 data source 时需要开启。
     - `Update content`：编辑已有 pages 和 database entries。更新 page properties、更新 block、trash page/block 时需要开启。
     - `Insert content`：创建新的 pages 和 database entries。创建 page、创建 database entry、插入 block、创建 child page/database 时需要开启。
   - Comment capabilities：
     - `Read comments`：查看 pages 和 blocks 上的 comments。读取 comments 时需要开启。
     - `Insert comments`：向 pages 和 blocks 添加 comments。创建 comment 或 reply comment 时需要开启。
   - User capabilities：
     - `No user information`：不允许读取 user 信息。
     - `Read user information without email addresses`：读取基础 user profile，不包含 email。通常足够用于 `notion-mcp auth whoami` 和身份校验。
     - `Read user information including email addresses`：读取包含 email 的 user profile。只有确实需要 email 时才开启。

3. 把 connection 授权到目标 page 或 database。
   - 方式一：在 Developer portal 的 Content access 页选择允许访问的 pages/databases。
   - 方式二：在 Notion 页面右上角 `...` 菜单中选择 Connections / Add connection，然后选择刚创建的 connection。
   - **授权父页面后，connection 通常可以访问该父页面下的 child pages。**
   - 如果 API 返回 403 或找不到对象，优先确认目标 page/database 是否已经 share 给该 connection。

4. 获取 page id。
   - 在 Notion 中打开目标页面。
   - 使用 Share / Copy link 复制页面链接。
   - URL 末尾的 32 位或带连字符 UUID 是 page id。
   - Notion API 通常接受带连字符或不带连字符的 UUID。
   - CLI 的 `<page_id>` 参数也可以直接传 Notion URL 或 Markdown 链接，例如：

```bash
notion-mcp page attach "https://www.notion.so/Notion-MCP-3799a1afb97a80489bb0e7384f334958?source=copy_link"
notion-mcp page retrieve "[Notion MCP](https://www.notion.so/Notion-MCP-3799a1afb97a80489bb0e7384f334958?source=copy_link)"
```

   - CLI 会自动解析出 page id，并保存为带连字符的 UUID。

5. 获取 database id。
   - 把 database 作为 full page 打开。
   - 使用 Share / Copy link 复制链接。
   - URL 中 workspace 名称后、查询参数 `?v=` 前的 32 位或 UUID 是 database id。
   - linked database 不是原始 database；如果使用 linked database，必须把原始 database 授权给 connection。

6. 获取 data source id。
   - 在当前 Notion API 中，database 是容器，data source 是 database 下的具体表。
   - 已配置 token 并授权 database 后，可运行：

```bash
notion-mcp database sources <database_id>
```

   - 也可以从 Notion UI 的 Manage data sources 菜单复制 data source id。
   - 如果 database 只有一个 data source，`database attach` 可以自动选择；如果有多个，必须显式传入 `--data-source <data_source_id_or_name>`。

7. 查看当前 token 对应身份。
   - 普通用户不需要手动填写 `user_id`。
   - 先写入全局 token，再调用 `auth whoami`：

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp auth whoami --json
```

   - JSON 输出中的 `user_id` 是当前 token 对应的 Notion identity id，仅用于排查和审计理解。
   - internal connection 通常返回 bot user id。
   - `notion-mcp auth validate` 会验证 token 是否可用。

参考官方文档：

- [Notion Internal connections](https://developers.notion.com/guides/get-started/internal-integrations)
- [Notion Developer quickstart](https://developers.notion.com/docs/create-a-notion-integration)
- [Notion Working with databases](https://developers.notion.com/guides/data-apis/working-with-databases)
- [Notion User object](https://developers.notion.com/reference/user)

## 全局配置

全局配置保存当前用户的 token、用户名、Notion API version、timeout、retry 等运行参数。默认写入：

```text
~/.notion_mcp/config.json
```

也可以通过环境变量指定其他路径：

```bash
NOTION_MCP_CONFIG=/path/to/config.json notion-mcp config --global --show
```

常用命令：

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global user.name "Ada"
notion-mcp config --global --show
notion-mcp config --global --show --json
```

`config --global --show` 会显示：

- 是否已经写入全局配置。
- token 是否已设置。
- 用户名称。
- Notion API version。

它不会输出 token 明文。

## 项目级配置

项目级配置让 CLI 像 Git 一样从当前目录向上查找项目上下文。这样在项目目录中工作时，不需要每次都手动输入 page id、database id 或 data source id。

项目级配置位于：

```text
.notion_mcp/config.json
```

项目级配置不保存 token。token 只保存在全局配置中。

初始化当前目录：

```bash
notion-mcp init --project-name "Demo"
notion-mcp init --workspace-hint "Team Workspace" --json
```

查看当前项目配置：

```bash
notion-mcp config --local --show
notion-mcp config --local --show --json
notion-mcp pwd
```

项目级配置示例：

```json
{
  "schema_version": 1,
  "project_name": "Demo",
  "workspace_hint": "Team Workspace",
  "settings": {
    "prefer_attached_page": true,
    "prefer_attached_database": true,
    "json_output_default": false
  }
}
```

## Page Attach

`page attach` 用于绑定当前项目默认 page，不是上传文件附件。

```bash
notion-mcp page attach <page_id>
notion-mcp page status
notion-mcp page retrieve
notion-mcp page blocks
```

取消绑定：

```bash
notion-mcp page detach
```

刷新本地状态：

```bash
notion-mcp page refresh
```

`page refresh` 只重新从 Notion 拉取标题、URL 和状态并更新本地状态，不修改 Notion 远端 page。

## Database Attach

Database 是容器，data source 是容器下的具体表。database attach 状态会保存当前绑定 database 和 active data source。

```bash
notion-mcp database attach <database_id>
notion-mcp database attach <database_id> --data-source <data_source_id_or_name>
notion-mcp database status
notion-mcp database query --payload '{"page_size": 10}'
```

取消绑定：

```bash
notion-mcp database detach
```

刷新本地状态：

```bash
notion-mcp database refresh
```

`database refresh` 只重新从 Notion 拉取 database 标题、URL、data sources 和状态并更新本地状态，不修改 Notion 远端 database。

## 常见工作流

设置全局 token 并初始化当前仓库：

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global user.name "Ada"
notion-mcp config --global --show
notion-mcp init --project-name "Demo"
notion-mcp config --local --show
```

绑定 page 后读取页面：

```bash
notion-mcp page attach <page_id>
notion-mcp page retrieve
notion-mcp page blocks --tree
```

绑定 database 后查询 active data source：

```bash
notion-mcp database attach <database_id> --data-source Tasks
notion-mcp database sources
notion-mcp database query --payload '{"page_size": 10}'
```

显式操作 data source：

```bash
notion-mcp data-source query <data_source_id> --payload '{"page_size": 10}'
notion-mcp data-source property rename <data_source_id> Status State
```

配置命令统一使用：

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global user.name "Ada"
notion-mcp config --global --show
```
