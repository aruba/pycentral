# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyCentral is a Python SDK (v2 pre-release) for HPE Aruba Networking Central REST APIs. It supports three platforms:
- **New Central** — latest platform, primary focus of v2
- **HPE GreenLake Platform (GLP)** — cloud management layer
- **Classic Central** — legacy v1 support in `pycentral/classic/`

## Common Commands

### Install for development
```bash
pip install -e .
```

### Install documentation dependencies
```bash
pip install -r docs/requirements.txt
```

### Build and serve documentation locally
```bash
mkdocs serve
mkdocs build
```

### Build distribution packages
```bash
python -m build
```

There are no automated tests in this repository. Contributors are expected to test manually before submitting PRs.

## Architecture

### Main Entry Point

`NewCentralBase` (`pycentral/base.py`) is the primary class — it handles connection, OAuth2 token management, and all HTTP requests. It's the only public export from `pycentral/__init__.py`.

### Module Structure

- **`pycentral/base.py`** — `NewCentralBase`: HTTP2 client (httpx), OAuth2 flow, automatic token refresh, exponential backoff retry (3 retries, 1–10s), credential loading from YAML/JSON
- **`pycentral/utils/`** — HTTP helpers, auth logic, token management, URL construction; shared across all modules
- **`pycentral/exceptions/`** — Exception hierarchy rooted at `PycentralError`: `LoginError`, `ParameterError`, `ResponseError`, `VerificationError`
- **`pycentral/scopes/`** — Hierarchical infrastructure model: `Scope → SiteCollection → Site → Device/DeviceGroup`; used for bulk operations across device groups
- **`pycentral/profiles/`** — Configuration profile abstraction; supports local (per-scope) and global profiles with a deep-copy modification pattern
- **`pycentral/new_monitoring/`** — Monitoring APIs for devices, APs, clients, gateways, sites on New Central
- **`pycentral/glp/`** — GLP-specific APIs: device management, subscriptions, service manager, user management
- **`pycentral/streaming/`** — WebSocket-based real-time event streaming with Protocol Buffer message definitions (audit, location, geofence, location_analytics)
- **`pycentral/classic/`** — Legacy v1 module (~600KB); all Classic Central API wrappers live here; avoid modifying unless fixing Classic-specific bugs

### Authentication

New Central requires `base_url` (or `cluster_name`) + `client_id` + `client_secret`. GLP requires only `client_id` + `client_secret`. Credentials can be passed as a dict or loaded from YAML/JSON files. See `sample_scripts/` for credential file templates.

## API Documentation

### Official References
- **New Central Config API:** https://developer.arubanetworks.com/new-central-config/reference
- **New Central API:** https://developer.arubanetworks.com/new-central/reference
- **Getting Started:** https://developer.arubanetworks.com/new-central/docs/getting-started-with-rest-apis

### Verifying Endpoints

Append `?json=on` to any reference page URL to retrieve the full OpenAPI 3.1.0 spec for that operation:

```bash
# Full spec for an operation
curl -s "https://developer.arubanetworks.com/new-central-config/reference/createsite?json=on"

# Extract request body schema
curl -s "https://developer.arubanetworks.com/new-central-config/reference/createsite?json=on" \
  | jq '.oasDefinition.components.schemas.SitePostRPCInputSchema'

# Extract endpoint path/method definition
curl -s "https://developer.arubanetworks.com/new-central-config/reference/getsites?json=on" \
  | jq '.oasDefinition.paths."/network-config/v1alpha1/sites".get'
```

Always verify exact endpoint paths, required vs. optional query parameters, request body schemas, and response schemas this way before implementing a new API wrapper.

## Contribution Guidelines

- All PRs must reference a GitHub issue number and target the **`v2(pre-release)`** branch (not main)
- Commits require DCO sign-off: `git commit -s`
- Code review from at least one maintainer required before merge
- Follow PEP-8; write docstrings in reStructuredText format
- New example scripts go in `sample_scripts/`; library code goes in `pycentral/`
- Test your changes manually before submitting — there is no automated test suite
