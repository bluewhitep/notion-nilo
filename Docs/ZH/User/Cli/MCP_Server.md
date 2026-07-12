# MCP Server CLI

本文说明本地 MCP server 的启动、停止、状态、日志和清理命令。

## Transport 契约

只支持 `stdio` 和 `streamable-http`。本地命令型 MCP client 使用 stdio；通过 URL 连接的本地或远程 MCP client 使用 Streamable HTTP。不支持 legacy SSE。

本版本只覆盖 localhost server 运行。远程部署、认证、TLS 和反向代理配置本轮延期；不要把无认证的示例 endpoint 暴露到网络。

## 后台 HTTP Server

| 命令 | 作用 |
| --- | --- |
| `nilo server run` | 后台启动 streamable-http MCP server。 |
| `nilo server status` | 查看后台 server 是否运行、PID、URL 和日志路径。 |
| `nilo server stop` | 停止后台 server 进程。 |
| `nilo server logs` | 查看后台 server 日志。 |
| `nilo server remove` | 停止 server 并移除本地 runtime state；默认同时删除日志。 |

后台 server 默认监听：

```bash
nilo server run --host 127.0.0.1 --port 8000
```

启动后 MCP URL 是：

```text
http://127.0.0.1:8000/mcp
```

常用管理命令：

```bash
nilo server status
nilo server logs --tail 100
nilo server stop
nilo server remove
```

如果停止时进程没有正常退出，可以使用：

```bash
nilo server stop --force
```

## Stdio Server

命令型 MCP client 如果需要由客户端拉起 stdio server，使用：

```bash
nilo server stdio
```

这个命令是前台进程。它会一直运行，直到 MCP client 关闭它，或用户在终端里按 `Ctrl+C`。

## 短别名

Server 命令有显式短别名，包括 `server/srv`、`run/start`、`stdio/pipe`、`status/stat`、`stop/halt`、`logs/tail` 和 `remove/rm`。

```bash
nilo srv start --host 127.0.0.1 --port 8000
nilo srv stat
nilo srv pipe
```

## Serve Alias

`nilo serve ...` 是 `nilo server ...` 的兼容别名。例如：

```bash
nilo serve run --host 127.0.0.1 --port 8000
```

正式文档优先使用 `nilo server ...`。

工具里的 MCP client 配置字段见 [MCP Clients](../MCP_Clients.md)。
