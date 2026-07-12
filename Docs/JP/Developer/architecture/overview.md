# アーキテクチャ概要

この文書は、現在の N.I.L.O. repository の実装境界を定義します。

## 目的

N.I.L.O. はローカル MCP server を提供します。実装は 2 つの共有 layer と 2 つの薄い adapter で構成されます。

- Core: 唯一の business logic layer。
- Runtime: business logic ではない共有 process/execution lifecycle layer。
- CLI: 人間向けの git-like local command interface。
- MCP server/tools: Agent/LLM 向けの structured adapter。

ユーザー向けのインストール、Notion connection 設定、コマンド利用方法は `Docs/JP/User/` にあります。この開発者 section は実装境界を記録します。

## 目標構造

```text
Human / Function Calling -> CLI adapter -> Core / Runtime
Agent / LLM -> MCP adapter -> Core / Runtime
```

必要な関係:

```text
CLI -> Core
CLI -> Runtime
MCP Tool -> Core
MCP Tool -> Runtime
```

禁止:

```text
CLI -> MCP
MCP -> CLI
Core または Runtime -> CLI または MCP
CLI -> Notion SDK
MCP Tool -> Notion SDK
```

## Core

Core は唯一の business logic layer です。責務は次の通りです。

- Global configuration の read/write、project context resolution、token redaction。
- Notion API version、timeout、retry の集中管理。
- Notion SDK-compatible client の作成。
- Auth validation と user/bot identity lookup。
- pages、blocks、databases、data sources、users、comments、views、file uploads、search、custom emojis の domain services。
- Raw API registry と controlled fallback calls。
- Local audit records と shared error model。

Core は global/project configuration の合成も担当します。effective configuration は global credentials を先に読み込み、user home より下にある最も近い project の credential-free overrides だけを適用します。project settings は global settings より優先され、token などの credentials は global-only です。

## Runtime

Runtime は managed server process state、log paths、background Streamable HTTP lifecycle、foreground stdio process startup など、domain に依存しない共有 execution behavior を持ちます。CLI/MCP adapters は Runtime を import できますが、Runtime は adapters を import してはいけません。

## CLI

CLI は人間向け entrypoint です。責務は次の通りです。

- Git-like command structure。
- Human-readable output。
- `--json` output。Function Calling 向けの stable one-line usage-error envelope を含みます。
- すべての public commands に 6 文字以内の明示的な alphabetic short alias。
- `--dry-run` preview。
- Local MCP server lifecycle commands。

公開 server commands:

```text
nilo server run
nilo server status
nilo server stop
nilo server logs
nilo server remove
nilo server stdio
```

CLI resource commands は Notion 操作に Core services、process lifecycle に Runtime を使います。CLI は MCP adapter を import してはいけません。

Project-local `.notion_mcp/` directory は project context、attachment state、credential-free setting overrides を保存し、token は保存しません。credentials は global configuration に保存します。project discovery は user home まで上位探索し、home の `.notion_mcp/` は global-only として扱います。project initialization は project root の `.gitignore` に `.notion_mcp/` を増分追加します。

## MCP Tool

MCP tools は Agent/LLM 向け entrypoint です。責務は次の通りです。

- Tool inventory。
- Input schemas。
- Tool annotations。
- Structured errors。
- Dangerous operations の confirmation requirements。

MCP tools は Core services を直接呼び出します。CLI command string は構築しません。

サポートする transport は、local command-launched client 用の `stdio` と URL-based service/client 接続用の `streamable-http` だけです。legacy SSE はサポートしません。remote deployment、authentication、TLS、reverse proxy configuration は今回は延期し、現在の server examples は local-only です。

## 非機能境界

- Tokens は通常の CLI output や MCP configuration status に表示してはいけません。
- CLI/MCP の write operations は、必要に応じて dry-run preview または dangerous-operation confirmation を持つ必要があります。
- Live tests は default skip とし、明示的な test page/database/data source/workspace に対してのみ実行します。
- Notion-Version は Core configuration で管理し、CLI、MCP tools、個別 services に散在させません。
- 共有 behavior は Core または Runtime に置き、CLI/MCP modules には adapter 固有 behavior だけを定義します。
