# File: src/nilo/core/config_constants.py
# Format: UTF-8
# =============================
# File Description:
# Shared Core configuration constants with no adapter-layer dependencies.
# TAG: core, config, constants, transport
# =============================

STDIO_TRANSPORT = "stdio"
STREAMABLE_HTTP_TRANSPORT = "streamable-http"
SUPPORTED_TRANSPORTS = (STDIO_TRANSPORT, STREAMABLE_HTTP_TRANSPORT)
DEFAULT_TRANSPORT = STDIO_TRANSPORT
