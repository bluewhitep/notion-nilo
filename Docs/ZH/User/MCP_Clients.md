# MCP Clients

本文说明如何在支持 MCP 的工具里配置 N.I.L.O. 本地 MCP server。

## 先配置 Notion Token

MCP client 不需要直接保存 Notion token。Notion token 保存在本机全局配置里：

```bash
nilo config --global user.token ntn_xxx
nilo config --global user.name "Ada"
nilo config --global --show
```

MCP 工具只需要连接本地 `nilo` server。

## 选择连接方式

N.I.L.O. 只支持以下两种 transport：

| 方式 | 适合场景 | 是否需要先手动启动 server |
| --- | --- | --- |
| stdio | 本地工具通过 command/args 自动拉起 MCP server | 不需要 |
| streamable-http | 本地或远程 client 连接 MCP 服务 URL | 需要先启动对应服务 |

本地命令型 client 使用 stdio。N.I.L.O. 作为服务运行、client 通过 URL 连接时使用 Streamable HTTP；client 可以在本地，也可以在远程。不支持 legacy SSE，transport 值 `sse` 会被拒绝。

## Stdio 配置

stdio 模式由 MCP 工具负责启动和停止 server。

工具里填写：

| 字段 | 值 |
| --- | --- |
| Server name | `nilo` |
| Transport | `stdio` |
| Command | `nilo` |
| Arguments | `server`, `stdio` |

如果工具使用 JSON 配置，常见格式是：

```json
{
  "mcpServers": {
    "nilo": {
      "command": "nilo",
      "args": ["server", "stdio"]
    }
  }
}
```

如果工具把参数写成一行，填：

```text
nilo server stdio
```

如果 `nilo` 是通过 `uv tool install .` 安装的，确保终端能直接运行：

```bash
nilo --help
```

如果工具找不到 `nilo`，先运行：

```bash
uv tool update-shell
```

然后重开终端或重启 MCP 工具。

## 未安装时的 Stdio 配置

如果还没有把 `nilo` 安装到 PATH，也可以让 MCP 工具通过 `uv` 从仓库路径临时运行。

工具里填写：

| 字段 | 值 |
| --- | --- |
| Server name | `nilo` |
| Transport | `stdio` |
| Command | `uv` |
| Arguments | `run`, `--no-project`, `--with`, `/path/to/notion-nilo`, `nilo`, `server`, `stdio` |

JSON 示例：

```json
{
  "mcpServers": {
    "nilo": {
      "command": "uv",
      "args": [
        "run",
        "--no-project",
        "--with",
        "/path/to/notion-nilo",
        "nilo",
        "server",
        "stdio"
      ]
    }
  }
}
```

把 `/path/to/notion-nilo` 替换成当前仓库根目录。

## Streamable HTTP 配置

如果工具支持 MCP URL 或 streamable-http，先在本机后台启动 server：

```bash
nilo server run --host 127.0.0.1 --port 8000
```

确认状态：

```bash
nilo server status
```

工具里填写：

| 字段 | 值 |
| --- | --- |
| Server name | `nilo` |
| Transport | `streamable-http` |
| URL | `http://127.0.0.1:8000/mcp` |
| Authentication | None（只适用于 localhost 示例） |

如果工具使用 JSON 配置，常见格式是：

```json
{
  "mcpServers": {
    "nilo": {
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

不要在工具里填写 Notion token。token 已由本地 `nilo` 配置读取。

## 远程服务范围

以后如果把 N.I.L.O. 部署为远程服务，transport 契约仍是 `/mcp` endpoint 上的 Streamable HTTP；远程 client 不得选择 legacy SSE。本版本只文档化并验证上面的 localhost server。远程部署、认证、TLS 和反向代理配置本轮延期，不要把这个无认证的 localhost 示例直接暴露到网络。

## 后台 Server 管理

查看状态：

```bash
nilo server status
```

查看日志：

```bash
nilo server logs --tail 100
```

停止：

```bash
nilo server stop
```

清理本地 server state 和日志：

```bash
nilo server remove
```

如果清理时需要强制停止 server，可以使用：

```bash
nilo server remove --force
```

这只清理后台 server runtime。若要从 MCP client 中移除 `nilo`，或继续卸载本地命令行工具、本地 token 和项目上下文，见 [Uninstallation](Uninstallation.md)。

## 环境变量

如果你使用自定义全局配置文件，MCP 工具也需要传入同样的环境变量：

```text
NOTION_MCP_CONFIG=/path/to/config.json
```

stdio JSON 示例：

```json
{
  "mcpServers": {
    "nilo": {
      "command": "nilo",
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

如果工具没有显示 N.I.L.O. MCP tools：

1. 先在终端运行 `nilo --help`，确认命令可用。
2. stdio 模式检查 command 和 args 是否分别填写，不要把整行命令都塞进 command 字段。
3. streamable-http 模式检查 `nilo server status` 是否显示 running。
4. 查看日志：`nilo server logs --tail 100`。
5. 确认 Notion token 已配置：`nilo config --global --show`。

## 安全说明

- token 保存在本地配置文件中，普通状态输出会脱敏。
- MCP 工具配置里不需要写 Notion token。
- `Authentication: None` 只适用于 `127.0.0.1`；本版本尚未定义远程部署安全方案。
- `page_trash`、`block_trash` 等危险工具需要 `confirm=true`。
- 真实 Notion 调用需要 connection 已被授权访问对应 page、database 或 workspace 内容。
