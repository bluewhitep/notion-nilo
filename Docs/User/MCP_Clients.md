# MCP Clients

本文说明如何在支持 MCP 的工具里配置本地 Notion MCP server。

## 先配置 Notion Token

MCP client 不需要直接保存 Notion token。Notion token 保存在本机全局配置里：

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global user.name "Ada"
notion-mcp config --global --show
```

MCP 工具只需要连接本地 `notion-mcp` server。

## 选择连接方式

常用连接方式有两种：

| 方式 | 适合场景 | 是否需要先手动启动 server |
| --- | --- | --- |
| stdio | 工具通过 command/args 自动拉起 MCP server | 不需要 |
| streamable-http | 工具连接一个本地 HTTP MCP URL | 需要先运行 `notion-mcp server run` |

优先使用工具支持的方式。如果工具支持 command/args，stdio 通常最简单。如果工具只支持 URL，使用 streamable-http。

## Stdio 配置

stdio 模式由 MCP 工具负责启动和停止 server。

工具里填写：

| 字段 | 值 |
| --- | --- |
| Server name | `notion-mcp` |
| Transport | `stdio` |
| Command | `notion-mcp` |
| Arguments | `server`, `stdio` |

如果工具使用 JSON 配置，常见格式是：

```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "notion-mcp",
      "args": ["server", "stdio"]
    }
  }
}
```

如果工具把参数写成一行，填：

```text
notion-mcp server stdio
```

如果 `notion-mcp` 是通过 `uv tool install .` 安装的，确保终端能直接运行：

```bash
notion-mcp --help
```

如果工具找不到 `notion-mcp`，先运行：

```bash
uv tool update-shell
```

然后重开终端或重启 MCP 工具。

## 未安装时的 Stdio 配置

如果还没有把 `notion-mcp` 安装到 PATH，也可以让 MCP 工具通过 `uv` 从仓库路径临时运行。

工具里填写：

| 字段 | 值 |
| --- | --- |
| Server name | `notion-mcp` |
| Transport | `stdio` |
| Command | `uv` |
| Arguments | `run`, `--no-project`, `--with`, `/path/to/notion_mcp_project`, `notion-mcp`, `server`, `stdio` |

JSON 示例：

```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--no-project",
        "--with",
        "/path/to/notion_mcp_project",
        "notion-mcp",
        "server",
        "stdio"
      ]
    }
  }
}
```

把 `/path/to/notion_mcp_project` 替换成当前仓库根目录。

## Streamable HTTP 配置

如果工具支持 MCP URL 或 streamable-http，先在本机后台启动 server：

```bash
notion-mcp server run --host 127.0.0.1 --port 8000
```

确认状态：

```bash
notion-mcp server status
```

工具里填写：

| 字段 | 值 |
| --- | --- |
| Server name | `notion-mcp` |
| Transport | `streamable-http` |
| URL | `http://127.0.0.1:8000/mcp` |
| Authentication | None |

如果工具使用 JSON 配置，常见格式是：

```json
{
  "mcpServers": {
    "notion-mcp": {
      "transport": "streamable-http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

如果工具的 transport 名称只提供 `http`、`streamableHttp` 或 `remote server` 之类选项，选择能填写 URL 的选项，并填：

```text
http://127.0.0.1:8000/mcp
```

不要在工具里填写 Notion token。token 已由本地 `notion-mcp` 配置读取。

## 后台 Server 管理

查看状态：

```bash
notion-mcp server status
```

查看日志：

```bash
notion-mcp server logs --tail 100
```

停止：

```bash
notion-mcp server stop
```

清理本地 server state 和日志：

```bash
notion-mcp server remove
```

如果停止失败，可以使用：

```bash
notion-mcp server stop --force
```

## 环境变量

如果你使用自定义全局配置文件，MCP 工具也需要传入同样的环境变量：

```text
NOTION_MCP_CONFIG=/path/to/config.json
```

stdio JSON 示例：

```json
{
  "mcpServers": {
    "notion-mcp": {
      "command": "notion-mcp",
      "args": ["server", "stdio"],
      "env": {
        "NOTION_MCP_CONFIG": "/path/to/config.json"
      }
    }
  }
}
```

## 当前 MCP Tool 清单

配置和认证：

- `config_status`
- `config_get`
- `auth_validate`
- `auth_whoami`

页面：

- `page_retrieve`
- `page_property_retrieve`
- `page_create`
- `page_update`
- `page_trash`

区块：

- `block_children_list`
- `block_append`
- `block_update`
- `block_trash`

数据库：

- `database_retrieve`
- `database_query`
- `database_create`
- `database_update`

数据源：

- `data_source_retrieve`
- `data_source_query`
- `data_source_create`
- `data_source_update`

用户：

- `user_me`
- `user_list`
- `user_retrieve`

评论：

- `comment_list`
- `comment_create`
- `comment_reply`

视图：

- `view_retrieve`
- `view_list`
- `view_query`
- `view_create`
- `view_update`

文件上传：

- `file_upload_retrieve`
- `file_upload_list`
- `file_upload_create`
- `file_upload_send`
- `file_upload_complete`

搜索和自定义表情：

- `search`
- `custom_emoji_list`
- `custom_emoji_retrieve`

受控 Raw API：

- `raw_api_registered_operations`
- `raw_api_invoke`

## 常见问题

如果工具没有显示 Notion MCP tools：

1. 先在终端运行 `notion-mcp --help`，确认命令可用。
2. stdio 模式检查 command 和 args 是否分别填写，不要把整行命令都塞进 command 字段。
3. streamable-http 模式检查 `notion-mcp server status` 是否显示 running。
4. 查看日志：`notion-mcp server logs --tail 100`。
5. 确认 Notion token 已配置：`notion-mcp config --global --show`。

## 安全说明

- token 保存在本地配置文件中，普通状态输出会脱敏。
- MCP 工具配置里不需要写 Notion token。
- `page_trash`、`block_trash` 等危险工具需要 `confirm=true`。
- 真实 Notion 调用需要 connection 已被授权访问对应 page、database 或 workspace 内容。
