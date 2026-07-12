# File: src/nilo/cli/core_services.py
# Format: UTF-8
# =============================
# File Description:
# CLI compatibility imports for Core-owned service constructors.
# TAG: cli, core-services, compatibility
# =============================

from nilo.core.services.provider import (
    get_blocks_service,
    get_comments_service,
    get_core_client,
    get_custom_emojis_service,
    get_data_sources_service,
    get_databases_service,
    get_file_uploads_service,
    get_pages_service,
    get_raw_api_service,
    get_search_service,
    get_users_service,
    get_views_service,
)

__all__ = [
    "get_blocks_service",
    "get_comments_service",
    "get_core_client",
    "get_custom_emojis_service",
    "get_data_sources_service",
    "get_databases_service",
    "get_file_uploads_service",
    "get_pages_service",
    "get_raw_api_service",
    "get_search_service",
    "get_users_service",
    "get_views_service",
]
