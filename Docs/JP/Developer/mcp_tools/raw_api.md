# Raw API Tools

- `raw_api_invoke`
  - 説明: Core registry で許可された Notion SDK/API operation を呼び出します。
  - Required parameters: `operation`.
  - Optional parameters: `arguments`, `confirm` (default `false`).
  - Security: `src/nilo/core/services/raw_api.py` に登録された operation だけを許可します。`blocks.delete`、または `archived=true` / `in_trash=true` を含む raw call は、Core を呼び出す前に `confirm=true` が必要です。
- `raw_api_registered_operations`
  - 説明: 呼び出し可能な raw API operations を一覧します。
  - Required parameters: none.
