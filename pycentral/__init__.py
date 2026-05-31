# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

__version__ = "2.0a20"

from .base import NewCentralBase
from .msp import MSPBase
# Manually import each module in the legacy Central folder
import importlib
import sys

CLASSIC_MODULES = [
    "audit_logs",
    "base",
    "base_utils",
    "configuration",
    "constants",
    "device_inventory",
    "firmware_management",
    "licensing",
    "monitoring",
    "msp",
    "rapids",
    "refresh_api_token",
    "topology",
    "url_utils",
    "user_management",
    "visualrf",
    "workflows",
]

for module in CLASSIC_MODULES:
    full_module_name = f"pycentral.classic.{module}"
    imported_module = importlib.import_module(full_module_name)

    sys.modules[f"pycentral.{module}"] = imported_module

# Delete importlib and sys to clean up the namespace after their use
del importlib, sys
