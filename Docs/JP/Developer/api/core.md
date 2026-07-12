# Core API

この文書は `src/nilo/core/` の現在の Core capability を記録します。Core は唯一の business logic layer です。CLI と MCP tools は Notion SDK を直接呼ばず、Core を呼び出します。

## Configuration

Module: `src/nilo/core/config.py`

- `CoreConfig`
  - `notion_token`、`user_name`、`user_id`、`notion_version`、`timeout_ms`、`retry`、`default_transport`、`audit_enabled` を保存します。
  - `user_id` が設定される場合は UUID である必要があります。
  - `notion_version` の default は `2026-03-11` です。
- `init_core_config(...)`
  - configuration を初期化し、local configuration file に書き込みます。
  - file permission は `0600` です。
- `load_global_core_config(...)`
  - project overrides を適用せず、global configuration だけを読み取ります。
- `load_core_config(...)`
  - effective configuration を返します。global credentials/settings を基準に、最も近い project の credential-free settings を重ねます。
  - project override は `notion_version`、`timeout_ms`、`retry`、`default_transport`、`audit_enabled` だけです。
- `resolve_config_locations(...)`
  - Git-like な上位 project search を行い、`ConfigLocations(project_dir, global_dir)` を返します。
  - start path が user-home tree 内にある場合、search は user home の手前で停止し、home は global-only です。
  - mounted volume など home tree 外の workspace では、その filesystem root に向かって上位探索しますが、root 自体を project として扱いません。
  - global lookup は project search から独立し、user home または `NOTION_MCP_CONFIG` だけを使います。project/global configuration が存在しない場合、それぞれ独立して `None` になります。
- `update_core_config(...)`
  - 渡された field だけを更新し、省略された field は消しません。
- `redacted_config(...)`
  - token を表示しない status-safe configuration を返します。

default global file は `~/.notion_mcp/config.json` で、`NOTION_MCP_CONFIG` により別の file を選べます。project configuration は active search boundary より下にある最も近い `.notion_mcp/config.json` で、home tree 外の workspace に置くこともできます。project settings は global settings より優先されますが、credentials は global-only です。project initialization は必要なら root `.gitignore` を作成し、既存内容を置き換えずに正確な `.notion_mcp/` entry を増分追加します。

## Error model

Module: `src/nilo/core/errors.py`

- `CoreError`
  - Core errors の base class。
  - `to_dict()` は `type`、`code`、`message`、`details` を返します。
- `ConfigNotFoundError`
- `ConfigValidationError`
- `NotionAuthError`
- `NotionOperationError`

CLI JSON output と MCP tool responses は、この error structure を再利用します。

## Notion SDK client

Module: `src/nilo/core/client.py`

- `NotionClientFactory`
  - `CoreConfig` から Notion SDK client を作成します。
  - `auth`、`notion_version`、`timeout_ms`、`retry` を注入します。
  - tests と MCP scenarios 向けに `client_cls` と `fake_client` をサポートします。
- `create_notion_client(...)`
  - default client factory entrypoint。

## Authentication

Module: `src/nilo/core/auth.py`

- `AuthService.validate(...)`
  - `client.users.me()` を呼び出して token を検証します。
  - `expected_user_id` を渡すと、configured user identity と current token identity を比較します。
  - `AuthValidationResult` を返します。

## Audit

Module: `src/nilo/core/audit.py`

- `AuditRecorder.record(...)`
  - JSONL audit records を書き込みます。
  - `timestamp`、`configured_user_id`、`operation`、`target`、`dry_run`、`metadata` を記録します。
  - `notion_token`、`token`、`auth`、`authorization`、`bearer` などの sensitive fields を除去します。

## Notion domain services

Directory: `src/nilo/core/services/`

Current service modules:

- `blocks.py`
- `pages.py`
- `databases.py`
- `data_sources.py`
- `users.py`
- `comments.py`
- `views.py`
- `file_uploads.py`
- `search.py`
- `custom_emojis.py`
- `raw_api.py`

これらの services は Core と Notion SDK-compatible client だけに依存します。CLI または MCP layer は import しません。

Module `src/nilo/core/services/provider.py` は client と domain services の canonical shared composition point です。CLI、MCP、compatibility adapters は独自 factory を持たず、この Core provider を import します。

## Shared Runtime API

Directory: `src/nilo/runtime/`

Runtime は adapters が共有する non-business execution behavior を持ちます。

- managed background Streamable HTTP server process の state、status、logs、stop、remove;
- foreground stdio server process startup;
- server command、runtime path、lifecycle helpers。

Runtime は Core contracts に依存できます。Core/Runtime は CLI/MCP adapters を import せず、CLI も MCP を import しません。

## Raw API

Module: `src/nilo/core/services/raw_api.py`

- `registered_operations()`
  - 許可された pass-through Notion SDK operation names を返します。
- `RawNotionService.invoke(operation, arguments)`
  - 登録済み operation だけを許可します。
  - 未登録 operation と private attributes を拒否します。
  - Supported public Notion SDK/API capabilities の controlled fallback を提供します。
