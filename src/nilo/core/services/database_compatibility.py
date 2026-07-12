# File: src/nilo/core/services/database_compatibility.py
# Format: UTF-8
# =============================
# File Description:
# Core orchestration for the ambiguous database/data-source legacy REST contract.
# TAG: core, services, database, compatibility
# =============================

from __future__ import annotations

from typing import Any

from ..errors import CoreError
from .base import BaseNotionService
from .data_sources import DataSourcesService
from .databases import DatabasesService
from .raw_api import RawNotionService
from .search import SearchService


class DatabaseCompatibilityService(BaseNotionService):
    # --------------------------------
    # Function Description:
    # Lists database or data-source search results for the legacy REST collection.
    # Inputs/Outputs:
    # Input supported Notion object kind; returns a search response dictionary.
    # Usage:
    # DatabaseCompatibilityService(client).list("data_source")
    # --------------------------------
    def list(self, kind: str) -> dict[str, Any]:
        return SearchService(self.client).search(
            {"filter": {"value": kind, "property": "object"}}
        )

    # --------------------------------
    # Function Description:
    # Retrieves an ambiguous legacy resource as a data source, then as a database.
    # Inputs/Outputs:
    # Input resource id; returns the first successful Core service response.
    # Usage:
    # DatabaseCompatibilityService(client).retrieve("resource-id")
    # --------------------------------
    def retrieve(self, resource_id: str) -> dict[str, Any]:
        try:
            return DataSourcesService(self.client).retrieve(resource_id)
        except CoreError:
            return DatabasesService(self.client).retrieve(resource_id)

    # --------------------------------
    # Function Description:
    # Queries an ambiguous legacy resource as a data source, then a database.
    # Inputs/Outputs:
    # Input resource id and payload; returns the first successful Core response.
    # Usage:
    # DatabaseCompatibilityService(client).query("resource-id", {"page_size": 10})
    # --------------------------------
    def query(self, resource_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = {
            key: value
            for key, value in (payload or {}).items()
            if key not in {"data_source_id", "database_id"}
        }
        try:
            return DataSourcesService(self.client).query(resource_id, data)
        except CoreError:
            return RawNotionService(self.client).invoke(
                "databases.query",
                {**data, "database_id": resource_id},
            )
