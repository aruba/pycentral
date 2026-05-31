# PyCentral Documentation

PyCentral is a Python SDK that makes it easier to interact with Central and the HPE GreenLake Platform (GLP) through REST APIs. Instead of building and managing low-level HTTP requests, developers can:

- Authenticate securely
- Configure and manage devices and subscriptions
- Monitor performance and collect analytics
- Run troubleshooting workflows

PyCentral handles authentication, request formatting, and error handling, while exposing simple Python functions. This lets you configure, monitor, and troubleshoot your network without dealing with raw REST API calls.

## Overview

PyCentral(v2) is the latest version of the SDK, designed for compatibility and simplicity:

- Backwards Compatible → Works with PyCentral v1 scripts, with no breaking changes.
- Multi-Platform Support → Works across Classic Central, New Central, and GLP.
- Use [MSPBase](modules/msp.md) for MSP-level and tenant-scoped API workflows with unified credentials.
- Simplified Token Management → Built-in OAuth2.0 support (no manual refresh needed).
- Simplified Automation → Modules for configuration, monitoring, devices, subscriptions, and troubleshooting.

## Versions

PyCentral-v2 is currently in pre-release, and we welcome feedback [here](https://github.com/aruba/pycentral/issues) as we continue improving it.
Today, there are two versions of PyCentral, each designed for different versions of Central

| Version                                                        | Supports                                                                                       | Notes                        |
| :------------------------------------------------------------- | :--------------------------------------------------------------------------------------------- | :--------------------------- |
| [v1](https://pypi.org/project/pycentral/)                      | Classic Central                                                 | Legacy Version               |
| [v2(pre-release)](https://pypi.org/project/pycentral/2.0a10/) | Central( or new Central), GLP, Classic Central | Backwards compatible with v1 |

## Quick Example

```python
from pycentral import NewCentralBase

central_credential = {
   "new_central": {
       "base_url": "https://us5.api.central.arubanetworks.com",
       "client_id": "client_id",
       "client_secret": "client_secret",
   }
}

# Initialize NewCentralBase class with the token credentials for Central/GLP
central_conn = NewCentralBase(token_info=central_credential)

# Central API Call
central_resp = central_conn.command(
    api_method="GET", api_path="network-monitoring/v1/devices"
)

# Check response status and print results or error message
if central_resp["code"] == 200:
    print(central_resp["msg"])
else:
    print(f"Error - Response code {central_resp['code']}")
    print(central_resp["msg"])

```

## Getting Started

- [Installation](getting-started/installation.md) - Install PyCentral
- [Authentication](getting-started/authentication.md) - Configure credentials
- [Quick Start](getting-started/quickstart.md) - Basic usage examples

## Module Documentation

Browse the complete module documentation:

- [Base Module](modules/base.md) - Core connection classes
- [Exceptions](modules/scopes.md) - Exceptions used throughout PyCentral
- [GLP](modules/glp.md) - HPE GreenLake Platform management
- [Monitoring](modules/new_monitoring.md) - Monitoring modules
- [MSP](modules/msp.md) - MSP modules
- [Profiles](modules/profiles.md) - Configuration profile management
- [Scopes](modules/scopes.md) - Scope management modules
- [Troubleshooting](modules/troubleshooting.md) - Troubleshooting Modules
- [Streaming](modules/streaming.md) - Streaming API Modules
- [Utils](modules/utils.md) - Utilities used throughout PyCentral
- [Classic](modules/classic.md) - Legacy PyCentral module reference

## License

MIT License - Copyright © 2025 Hewlett Packard Enterprise Development LP
