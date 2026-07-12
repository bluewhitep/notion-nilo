# File: src/nilo/models/config_model.py
# Format: UTF-8
# =============================
# File Description:
# Legacy Config symbol re-exporting the canonical Core configuration model.
# TAG: compatibility, models, config, core
# =============================

from nilo.core.config import CoreConfig

Config = CoreConfig

__all__ = ["Config"]
