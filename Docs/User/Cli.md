# CLI 文档目录

本文是 `notion-mcp` CLI 的使用入口。具体命令已经按主题拆分到下方分册，避免把 page、block、database、配置和高级入口混在同一个文件里。

## 先读

- [Installation](Installation.md)：安装 `notion-mcp`。
- [Configuration](Configuration.md)：准备 Notion connection、设置 token、创建项目级上下文。
- [MCP Clients](MCP_Clients.md)：在 MCP 工具里配置本地 Notion MCP server。
- [Troubleshooting](Troubleshooting.md)：常见错误和排查入口。

## CLI 分册

- [Overview](Cli/Overview.md)：通用规则、JSON 参数、`--dry-run` 和命令别名。
- [Project Config](Cli/Project_Config.md)：`init`、`pwd`、`version` 和 `config --global/--local`。
- [Page](Cli/Page.md)：绑定默认 page、读取 page、读取 blocks、创建和更新 page。
- [Block](Cli/Block.md)：append、insert-after、update、trash 等 block 操作。
- [Database DataSource](Cli/Database_DataSource.md)：database 容器、data source 表级操作和 database 快捷命令。
- [Auth And User](Cli/Auth_And_User.md)：token 校验、whoami 和 user 查询。
- [Comments](Cli/Comments.md)：读取、创建和回复 comments。
- [Views](Cli/Views.md)：读取、列出、查询、创建和更新 views。
- [File Uploads](Cli/File_Uploads.md)：file upload 生命周期命令。
- [Search And Custom Emoji](Cli/Search_And_Custom_Emoji.md)：workspace 搜索和 custom emoji。
- [Raw API](Cli/Raw_API.md)：高级兜底 Raw API 入口。
- [MCP Server](Cli/MCP_Server.md)：启动、停止、查看状态和日志。

## 常用起步顺序

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global --show
notion-mcp init --project-name "Demo"
notion-mcp page attach <page_id>
notion-mcp page retrieve
notion-mcp page blocks
```
