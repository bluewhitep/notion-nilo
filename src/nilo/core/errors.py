# File: src/nilo/core/errors.py
# Format: UTF-8
# =============================
# File Description:
# Unified Core error types shared by CLI, REST compatibility code, and MCP tools.
# TAG: core, errors
# =============================

from __future__ import annotations

from typing import Any


# --------------------------------
# Function Description:
# Converts arbitrary error details into values supported by standard JSON encoders.
# Inputs/Outputs:
# Input nested detail value; returns scalar/list/dictionary data with unknown objects stringified.
# Usage:
# _json_safe({"error": ValueError("bad")})
# --------------------------------
def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(nested) for key, nested in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(nested) for nested in value]
    return str(value)


class CoreError(Exception):
    default_code = "core_error"

    # --------------------------------
    # Function Description:
    # Initializes a serializable Core error.
    # Inputs/Outputs:
    # Input message/code/details; output is an exception with stable public fields.
    # Usage:
    # CoreError("failed", code="example").to_dict()
    # --------------------------------
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        self.details = details or {}

    # --------------------------------
    # Function Description:
    # Serializes an error for CLI JSON and MCP structured responses.
    # Inputs/Outputs:
    # No input; returns a dictionary with type, code, message, and details.
    # Usage:
    # error.to_dict()
    # --------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": _json_safe(self.details),
        }


class ConfigNotFoundError(CoreError):
    default_code = "config_not_found"

    # --------------------------------
    # Function Description:
    # Builds an error for a missing local configuration file.
    # Inputs/Outputs:
    # Input path string; output is ConfigNotFoundError with path details.
    # Usage:
    # raise ConfigNotFoundError("/tmp/config.json")
    # --------------------------------
    def __init__(self, path: str) -> None:
        super().__init__(
            f"Configuration file does not exist: {path}",
            details={"path": path},
        )


class ConfigValidationError(CoreError):
    default_code = "config_validation_failed"

    # --------------------------------
    # Function Description:
    # Builds an error for invalid Core configuration data.
    # Inputs/Outputs:
    # Input message/details; output is ConfigValidationError.
    # Usage:
    # raise ConfigValidationError("Invalid user_id")
    # --------------------------------
    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)


class ProjectConfigNotFoundError(CoreError):
    default_code = "project_config_not_found"

    # --------------------------------
    # Function Description:
    # Builds an error for a missing project-level configuration file.
    # Inputs/Outputs:
    # Input start path; output is ProjectConfigNotFoundError with remediation details.
    # Usage:
    # raise ProjectConfigNotFoundError("/workspace/project")
    # --------------------------------
    def __init__(self, start: str) -> None:
        super().__init__(
            "No .notion_mcp/config.json found from current directory or its parents.\n"
            "Run:\n"
            "  nilo init\n"
            "Or attach a page, which will initialize project context:\n"
            "  nilo page attach <page_id>",
            details={"start": start},
        )


class ProjectAlreadyInitializedError(CoreError):
    default_code = "project_already_initialized"

    # --------------------------------
    # Function Description:
    # Builds an error when project init would overwrite an existing config.
    # Inputs/Outputs:
    # Input config path; output is ProjectAlreadyInitializedError.
    # Usage:
    # raise ProjectAlreadyInitializedError("/workspace/.notion_mcp/config.json")
    # --------------------------------
    def __init__(self, path: str) -> None:
        super().__init__(
            f"Project already initialized: {path}",
            details={"path": path},
        )


class ProjectConfigValidationError(CoreError, ValueError):
    default_code = "project_config_validation_failed"

    # --------------------------------
    # Function Description:
    # Builds an error for invalid project-level configuration data.
    # Inputs/Outputs:
    # Input message/details; output is ProjectConfigValidationError.
    # Usage:
    # raise ProjectConfigValidationError("Project config must not contain token fields")
    # --------------------------------
    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)


class PageAttachmentNotFoundError(CoreError):
    default_code = "page_attachment_not_found"

    # --------------------------------
    # Function Description:
    # Builds an error when a command needs an attached page but no state exists.
    # Inputs/Outputs:
    # Input project root string; output is PageAttachmentNotFoundError.
    # Usage:
    # raise PageAttachmentNotFoundError("/workspace/project")
    # --------------------------------
    def __init__(self, project_root: str) -> None:
        super().__init__(
            "No page is attached for this project.\n"
            "Run:\n"
            "  nilo page attach <page_id>\n"
            "Or pass page_id explicitly:\n"
            "  nilo page retrieve <page_id>",
            details={"project_root": project_root},
        )


class DatabaseAttachmentNotFoundError(CoreError):
    default_code = "database_attachment_not_found"

    # --------------------------------
    # Function Description:
    # Builds an error when a command needs an attached database but no state exists.
    # Inputs/Outputs:
    # Input project root string; output is DatabaseAttachmentNotFoundError.
    # Usage:
    # raise DatabaseAttachmentNotFoundError("/workspace/project")
    # --------------------------------
    def __init__(self, project_root: str) -> None:
        super().__init__(
            "No database is attached for this project.\n"
            "Run:\n"
            "  nilo database attach <database_id>\n"
            "Or pass id explicitly:\n"
            "  nilo database retrieve <database_id>",
            details={"project_root": project_root},
        )


class ActiveDataSourceNotFoundError(CoreError):
    default_code = "active_data_source_not_found"

    # --------------------------------
    # Function Description:
    # Builds an error when a table-level command needs an active data source.
    # Inputs/Outputs:
    # Input project root/database id; output is ActiveDataSourceNotFoundError.
    # Usage:
    # raise ActiveDataSourceNotFoundError("/workspace/project", "database-id")
    # --------------------------------
    def __init__(self, project_root: str, database_id: str | None = None) -> None:
        super().__init__(
            "Attached database has no active data source.\n"
            "This command requires a data source.\n"
            "Run:\n"
            "  nilo database status --refresh\n"
            "Or:\n"
            "  nilo database attach <database_id> --data-source <data_source_id_or_name>",
            details={"project_root": project_root, "database_id": database_id},
        )


class DatabaseDataSourceSelectionError(CoreError):
    default_code = "database_data_source_selection_required"

    # --------------------------------
    # Function Description:
    # Builds an error when database attach cannot choose one active data source.
    # Inputs/Outputs:
    # Input database id, source list, and optional selector; output is CoreError.
    # Usage:
    # raise DatabaseDataSourceSelectionError("db", sources=[], selector=None)
    # --------------------------------
    def __init__(
        self,
        database_id: str,
        *,
        sources: list[dict[str, Any]],
        selector: str | None,
    ) -> None:
        source_lines = "\n".join(
            f"  {index}. {source.get('name') or ''} {source.get('id') or ''}".rstrip()
            for index, source in enumerate(sources, start=1)
        )
        if selector:
            message = (
                f"Data source selector did not match this database: {selector}\n"
                f"Database: {database_id}\n"
                f"Data sources:\n{source_lines}"
            )
        else:
            message = (
                "This database contains multiple data sources.\n"
                f"Database: {database_id}\n"
                f"Data sources:\n{source_lines}\n"
                "Please attach again with:\n"
                "  nilo database attach <database_id> --data-source <data_source_id_or_name>"
            )
        super().__init__(
            message,
            details={"database_id": database_id, "sources": sources, "selector": selector},
        )


class NotionAuthError(CoreError):
    default_code = "notion_auth_failed"

    # --------------------------------
    # Function Description:
    # Builds an error for Notion token validation failures.
    # Inputs/Outputs:
    # Input message/details; output is NotionAuthError.
    # Usage:
    # raise NotionAuthError("Invalid token")
    # --------------------------------
    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)


class NotionOperationError(CoreError):
    default_code = "notion_operation_failed"

    # --------------------------------
    # Function Description:
    # Builds an error for a failed Notion SDK operation.
    # Inputs/Outputs:
    # Input operation/message/details; output is NotionOperationError.
    # Usage:
    # raise NotionOperationError("pages.retrieve", "failed")
    # --------------------------------
    def __init__(
        self,
        operation: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        merged_details = {"operation": operation}
        if details:
            merged_details.update(details)
        super().__init__(message, details=merged_details)
