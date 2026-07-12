# File: src/nilo/core/services/provider.py
# Format: UTF-8
# =============================
# File Description:
# Canonical Core client and service constructors shared by adapters.
# TAG: core, services, provider, dependency-injection
# =============================

from __future__ import annotations

from typing import Any

from ..client import create_notion_client
from ..config import CoreConfig, load_core_config
from .blocks import BlocksService
from .comments import CommentsService
from .custom_emojis import CustomEmojisService
from .data_sources import DataSourcesService
from .database_compatibility import DatabaseCompatibilityService
from .databases import DatabasesService
from .file_uploads import FileUploadsService
from .pages import PagesService
from .raw_api import RawNotionService
from .search import SearchService
from .users import UsersService
from .views import ViewsService


# --------------------------------
# Function Description:
# Creates a Notion client from explicit or locally loaded Core configuration.
# Inputs/Outputs:
# Optional CoreConfig; returns an SDK-compatible client.
# Usage:
# get_core_client()
# --------------------------------
def get_core_client(config: CoreConfig | None = None) -> Any:
    return create_notion_client(config if config is not None else load_core_config())


# --------------------------------
# Function Description:
# Resolves an explicitly injected client or creates the configured Core client.
# Inputs/Outputs:
# Optional client; returns that client or a newly configured client.
# Usage:
# _resolve_client(fake_client)
# --------------------------------
def _resolve_client(client: Any | None) -> Any:
    return client if client is not None else get_core_client()


# --------------------------------
# Function Description:
# Creates the Core pages service.
# Inputs/Outputs:
# Optional injected client; returns PagesService.
# Usage:
# get_pages_service()
# --------------------------------
def get_pages_service(client: Any | None = None) -> PagesService:
    return PagesService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core blocks service.
# Inputs/Outputs:
# Optional injected client; returns BlocksService.
# Usage:
# get_blocks_service()
# --------------------------------
def get_blocks_service(client: Any | None = None) -> BlocksService:
    return BlocksService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core databases service.
# Inputs/Outputs:
# Optional injected client; returns DatabasesService.
# Usage:
# get_databases_service()
# --------------------------------
def get_databases_service(client: Any | None = None) -> DatabasesService:
    return DatabasesService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core data-sources service.
# Inputs/Outputs:
# Optional injected client; returns DataSourcesService.
# Usage:
# get_data_sources_service()
# --------------------------------
def get_data_sources_service(client: Any | None = None) -> DataSourcesService:
    return DataSourcesService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core legacy database compatibility service.
# Inputs/Outputs:
# Optional injected client; returns DatabaseCompatibilityService.
# Usage:
# get_database_compatibility_service()
# --------------------------------
def get_database_compatibility_service(
    client: Any | None = None,
) -> DatabaseCompatibilityService:
    return DatabaseCompatibilityService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core users service.
# Inputs/Outputs:
# Optional injected client; returns UsersService.
# Usage:
# get_users_service()
# --------------------------------
def get_users_service(client: Any | None = None) -> UsersService:
    return UsersService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core comments service.
# Inputs/Outputs:
# Optional injected client; returns CommentsService.
# Usage:
# get_comments_service()
# --------------------------------
def get_comments_service(client: Any | None = None) -> CommentsService:
    return CommentsService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core views service.
# Inputs/Outputs:
# Optional injected client; returns ViewsService.
# Usage:
# get_views_service()
# --------------------------------
def get_views_service(client: Any | None = None) -> ViewsService:
    return ViewsService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core file-uploads service.
# Inputs/Outputs:
# Optional injected client; returns FileUploadsService.
# Usage:
# get_file_uploads_service()
# --------------------------------
def get_file_uploads_service(client: Any | None = None) -> FileUploadsService:
    return FileUploadsService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core search service.
# Inputs/Outputs:
# Optional injected client; returns SearchService.
# Usage:
# get_search_service()
# --------------------------------
def get_search_service(client: Any | None = None) -> SearchService:
    return SearchService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core custom-emojis service.
# Inputs/Outputs:
# Optional injected client; returns CustomEmojisService.
# Usage:
# get_custom_emojis_service()
# --------------------------------
def get_custom_emojis_service(client: Any | None = None) -> CustomEmojisService:
    return CustomEmojisService(_resolve_client(client))


# --------------------------------
# Function Description:
# Creates the Core raw API service.
# Inputs/Outputs:
# Optional injected client; returns RawNotionService.
# Usage:
# get_raw_api_service()
# --------------------------------
def get_raw_api_service(client: Any | None = None) -> RawNotionService:
    return RawNotionService(_resolve_client(client))
