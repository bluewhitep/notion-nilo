# CLI Overview

本文说明 `nilo` CLI 的通用规则。

## 通用规则

- 查看帮助时，`-h` 与 `--help` 等价，例如 `nilo -h`、`nilo page -h`。
- 大多数读取命令支持 `--json`，用于给脚本或 Agent 读取结构化结果。
- 写入、更新、发送、完成、trash 等有副作用命令优先使用 `--dry-run` 预览请求。
- JSON 参数通过 `--payload`、`--properties` 或 `--arguments` 传入，内容必须是 JSON object。
- `page/pages`、`block/blocks`、`database/databases` 等复数形式是别名；用户文档默认写单数形式。
- 与 Git 或 gh 类似，全局命令可以在任意目录运行；项目级命令向上查到用户根目录，并使用最近的 `.notion_mcp/`。
- 真实调用前，需要先用 `nilo config --global user.token <token>` 设置全局 token，并确保 Notion connection 已被授权访问目标页面、数据库或 workspace 内容。

## 短别名

每个公开命令还有一个显式英文字母短别名，长度不超过六个字符。文档仍以规范全称为主。例如：

```bash
nilo cfg --global --show
nilo pg get <page_id> --json
nilo srv start --host 127.0.0.1 --port 8000
```

常用 root 别名包括 `init/ini`、`version/ver`、`config/cfg`、`pwd/cwd`、`page/pg`、`block/blk`、`database/db`、`data-source/ds` 和 `server/srv`。

## Function Calling JSON 错误

Function Calling 应带上 `--json`。如果 option 不存在、必需参数缺失或参数无效，CLI 会输出且只输出一行紧凑 JSON，并提供稳定错误码，而不是输出 Rich help。不带 `--json` 的调用继续保留适合人类阅读的 help 和错误格式。

```json
{"ok":false,"error":{"type":"CliUsageError","code":"cli_missing_parameter","message":"...","details":{"exit_code":2}}}
```

## JSON 参数示例

```bash
nilo page update <page_id> --payload '{"properties": {}}'
nilo database query --payload '{"page_size": 10}'
nilo raw-api invoke search --arguments '{"query": "Tasks"}' --json
```

## 副作用命令预览

```bash
nilo block append <block_id> --payload '{"children": []}' --dry-run --json
nilo block trash <block_id> --dry-run
```
