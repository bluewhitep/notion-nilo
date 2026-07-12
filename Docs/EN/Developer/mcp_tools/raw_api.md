# Raw API Tools

- `raw_api_invoke`
  - Description: calls a Notion SDK/API operation allowed by the Core registry.
  - Required parameters: `operation`.
  - Optional parameters: `arguments`, `confirm` (default `false`).
  - Security: only operations registered in `src/nilo/core/services/raw_api.py` are allowed. Arbitrary attribute traversal is rejected. `blocks.delete` and any raw call with `archived=true` or `in_trash=true` require `confirm=true` before Core is invoked.
- `raw_api_registered_operations`
  - Description: lists callable raw API operations.
  - Required parameters: none.
