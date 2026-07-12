# Project Config CLI

本文说明项目上下文和配置相关命令。

## 命令

| 命令 | 作用 |
| --- | --- |
| `nilo init` | 在当前目录创建项目级 `.notion_mcp/`，用于记录当前目录的 Notion 上下文。 |
| `nilo pwd` | 从当前目录向上查找项目配置，并输出解析到的项目根目录。 |
| `nilo version` | 显示 N.I.L.O. 版本和当前配置的 Notion API version。 |
| `nilo config --global --show` | 查看全局配置状态：是否已配置、token 是否已设置、用户名称和 Notion API version。 |
| `nilo config --global user.token <token>` | 设置当前用户级 Notion token。 |
| `nilo config --global user.name <name>` | 设置当前用户级显示名称。 |
| `nilo config --local --show` | 查看当前仓库或目录树的项目级配置。 |

## 示例

```bash
nilo init --project-name "Demo"
nilo pwd
nilo version --json
nilo config --global user.token ntn_xxx
nilo config --global user.name "Ada"
nilo config --global --show
nilo config --local --show --json
```

全局配置保存 token 和运行参数；项目级配置不保存 token。普通用户不需要手动填写 `user_id`，需要查看当前 token 身份时使用 `nilo auth whoami --json`。

## 路径与优先级

- 全局目录：`~/.notion_mcp/`；全局文件：`~/.notion_mcp/config.json`。`NOTION_MCP_CONFIG` 可以指定其他全局文件。
- 项目目录：`<project-root>/.notion_mcp/`；项目文件：`<project-root>/.notion_mcp/config.json`。
- 有效的非敏感设置采用“项目级 > 全局”的优先级。
- 项目只允许覆盖 `notion_version`、`timeout_ms`、`retry`、`default_transport` 和 `audit_enabled`。
- token 与其他凭据只能保存在全局配置中，不会从项目配置读取。

## 向上查询配置位置

当前目录位于用户 home 树内时，配置位置接口向上查到 home，但不把 home 本身作为项目。home 以下最近的 `.notion_mcp/config.json` 是项目级配置；home 自身的 `.notion_mcp/` 只算全局配置。

workspace 位于 home 树外（例如外接磁盘或挂载目录）时，项目查找向上到该文件系统根之前，使 Git-like 项目命令仍然可用；文件系统根本身绝不作为项目。全局查找不会跟随这条外部路径，仍然只使用用户 home 或 `NOTION_MCP_CONFIG`。

返回结果分别表达两个位置：

- 没有项目文件时：`project_dir=None`；
- 没有全局文件，包括 `~/.notion_mcp/config.json` 不存在时：`global_dir=None`；
- 只有用户根目录的全局文件时：`project_dir=None`，`global_dir=~/.notion_mcp`。

## 初始化与 Git Ignore

`nilo init` 不允许把用户根目录初始化为项目。在有效项目根中，它会创建 `.notion_mcp/`；如果根 `.gitignore` 不存在则创建，并增量加入精确条目 `.notion_mcp/`。已有内容会保留，重复初始化不会写入重复条目。
