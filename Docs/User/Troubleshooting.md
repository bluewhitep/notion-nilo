# Troubleshooting

本文面向使用者，记录常见问题。

## 未配置 token

运行：

```bash
notion-mcp config --global user.token ntn_xxx
notion-mcp config --global user.name "Ada"
```

然后检查：

```bash
notion-mcp config --global --show
```

## token 无权限

确认 Notion integration 已被授权访问目标页面、数据库或 workspace 内容。

## 用户身份不匹配

普通用户不需要手动填写 `user_id`。如果高级配置中已经设置了 `user_id`，且 `auth validate` 报告用户不匹配，请先运行：

```bash
notion-mcp auth whoami --json
```

确认当前 token 对应的 Notion identity 是否符合预期。

## MCP client 无法启动

先在终端确认：

```bash
notion-mcp server stdio --help
notion-mcp server run --help
```

client 配置应使用：

```json
{
  "command": "notion-mcp",
  "args": ["server", "stdio"]
}
```

如果使用后台 streamable-http server，检查：

```bash
notion-mcp server status
notion-mcp server logs --tail 100
```

## Notion API version 问题

当前默认使用 `2026-03-11`。如果调用参数与 Notion 返回错误不匹配，请检查 Notion API 文档对应版本的字段名。

## Rate limit

如果遇到 rate limit，请降低调用频率，或让 Agent 分批执行操作。
