# MCP Server CLI

本文说明本地 MCP server 的启动、停止、状态、日志和清理命令。

## 后台 HTTP Server

| 命令 | 作用 |
| --- | --- |
| `notion-mcp server run` | 后台启动 streamable-http MCP server。 |
| `notion-mcp server status` | 查看后台 server 是否运行、PID、URL 和日志路径。 |
| `notion-mcp server stop` | 停止后台 server 进程。 |
| `notion-mcp server logs` | 查看后台 server 日志。 |
| `notion-mcp server remove` | 停止 server 并移除本地 runtime state；默认同时删除日志。 |

后台 server 默认监听：

```bash
notion-mcp server run --host 127.0.0.1 --port 8000
```

启动后 MCP URL 是：

```text
http://127.0.0.1:8000/mcp
```

常用管理命令：

```bash
notion-mcp server status
notion-mcp server logs --tail 100
notion-mcp server stop
notion-mcp server remove
```

如果停止时进程没有正常退出，可以使用：

```bash
notion-mcp server stop --force
```

## Stdio Server

命令型 MCP client 如果需要由客户端拉起 stdio server，使用：

```bash
notion-mcp server stdio
```

这个命令是前台进程。它会一直运行，直到 MCP client 关闭它，或用户在终端里按 `Ctrl+C`。

## Serve Alias

`notion-mcp serve ...` 是 `notion-mcp server ...` 的兼容别名。例如：

```bash
notion-mcp serve run --host 127.0.0.1 --port 8000
```

正式文档优先使用 `notion-mcp server ...`。

工具里的 MCP client 配置字段见 [MCP Clients](../MCP_Clients.md)。
