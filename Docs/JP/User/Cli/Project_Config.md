# Project Config CLI

このページでは project context と configuration commands を説明します。

## コマンド

| Command | Purpose |
| --- | --- |
| `nilo init` | 現在の directory に project-local `.notion_mcp/` context を作成します。 |
| `nilo pwd` | 現在の directory から上位へ探索し、project root を解決します。 |
| `nilo version` | package version と configured Notion API version を表示します。 |
| `nilo config --global --show` | token を表示せず、global configuration status を表示します。 |
| `nilo config --global user.token <token>` | user-level Notion token を設定します。 |
| `nilo config --global user.name <name>` | user-level display name を設定します。 |
| `nilo config --local --show` | 現在の directory tree の project-local configuration を表示します。 |

## 例

```bash
nilo init --project-name "Demo"
nilo pwd
nilo version --json
nilo config --global user.token ntn_xxx
nilo config --global user.name "Ada"
nilo config --global --show
nilo config --local --show --json
```

グローバル設定は token と runtime settings を保存します。project-local configuration は token を保存しません。通常の利用では `user_id` の設定は不要です。現在の token identity を確認する場合は `nilo auth whoami --json` を使います。

## Paths and precedence

- Global directory: `~/.notion_mcp/`; global file: `~/.notion_mcp/config.json`。`NOTION_MCP_CONFIG` で別の global file を選べます。
- Project directory: `<project-root>/.notion_mcp/`; project file: `<project-root>/.notion_mcp/config.json`。
- effective non-sensitive settings は project values を global values より優先します。
- project overrides は `notion_version`、`timeout_ms`、`retry`、`default_transport`、`audit_enabled` だけです。
- token その他の credentials は global-only で、project configuration から読み取りません。

## Configuration location の上位探索

current directory が user-home tree 内にある場合、location API は home まで上位探索しますが、home 自体を project として扱いません。home より下にある最も近い `.notion_mcp/config.json` が project configuration で、home 自体の `.notion_mcp/` は global-only です。

workspace が external disk や mounted directory など home tree 外にある場合、Git-like project commands を利用できるよう、その filesystem root に向かって上位探索します。ただし filesystem root 自体は project として扱いません。global lookup はこの external path をたどらず、user home または `NOTION_MCP_CONFIG` だけを使います。

result は 2 つの location を独立して表現します。

- project file がない場合: `project_dir=None`;
- `~/.notion_mcp/config.json` がない場合を含め、global file がない場合: `global_dir=None`;
- home-level global file だけがある場合: `project_dir=None`、`global_dir=~/.notion_mcp`。

## Initialization and Git ignore

`nilo init` は user home を project として初期化できません。有効な project root では `.notion_mcp/` を作成し、必要なら root `.gitignore` も作成して、正確な `.notion_mcp/` line を増分追加します。既存 content は保持され、再実行しても entry は重複しません。
