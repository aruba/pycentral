# 2.0a25

This release expands Streaming API support for client, switch, and alert events, and improves profile initialization with configurable API paths.

### New Features

- **Expanded Streaming API Support**
  - Added support & decoders for clients, switch, and alert streaming topics.
  - Streaming WebSocket URLs now resolve the appropriate service path and API version for each supported event topic.
  - Updated Streaming API documentation with the complete supported-topic list.

### Improvements

- **Profile Path Initialization**
  - `Profiles` now accepts an optional `path` parameter during initialization.
  - When a profile name is supplied, the path is normalized to include the URL-encoded name when required.

Full Changelog: [v2.0a24...v2.0a25](https://github.com/aruba/pycentral/compare/v2.0a24...v2.0a25)

# 2.0a24

This release adds support for Central On-Prem (3.x) deployments.

### New Features
- **Central On-Prem (3.x) Support**
  - Added `token_endpoint` attribute to support Central On-Prem instance as the OAuth issuer differs from the standard GLP OAuth issuer.
  - Uses the configured endpoint for initial token creation and automatic token renewal.
  - Documented Central On-Prem (3.x) authentication configuration and clarified that this option is supported under `new_central`.
Full Changelog: [v2.0a23...v2.0a24](https://github.com/aruba/pycentral/compare/v2.0a23...v2.0a24)

# 2.0a23

This release updates package dependency constraints to allow compatible dependency updates while preserving major-version guardrails, and aligns device attribute mapping with the latest API response fields.

### Improvements

- **Dependency Version Constraints**
  - Relaxed runtime dependencies from exact pins to bounded version ranges in `pyproject.toml`, allowing compatible patch and minor updates while preserving upper bounds
  - Added bounded version constraints for the optional `colorLog` extra

### API Compatibility

- **Device Attribute Mapping**
  - Updated the device API attribute mapping to use the API's `firmwareVersion` field and the `firmware-version` attribute name

Full Changelog: [v2.0a22...v2.0a23](https://github.com/aruba/pycentral/compare/v2.0a22...v2.0a23)

# 2.0a22

This release adds AP event streaming support via a new `network-monitoring` service category, with dynamic protobuf dispatch for AP event types.

### New Features

- **AP Events Streaming**
  - Added `ap-events` to the streaming module under the new `network-monitoring` service path
  - Added `pycentral/streaming/events/ap/ap_events_pb2.py` — generated protobuf definitions for AP event messages (e.g. `APInfo`, `ClusterInfo`)
  - The `Streaming` client now dynamically resolves the AP event message class from the CloudEvent `type_url`, first via the protobuf symbol database and falling back to a direct attribute lookup on `ap_events_pb2`

### Improvements

- **Streaming `SUPPORTED_EVENTS` restructured**
  - Flat event dict replaced by a nested structure keyed by URL service path (`network-services`, `network-monitoring`), enabling correct WebSocket URL construction per event category
  - WebSocket URL is now built dynamically from the service group the requested event belongs to, fixing the URL for `network-monitoring` events

Full Changelog: [v2.0a21...v2.0a22](https://github.com/aruba/pycentral/compare/v2.0a21...v2.0a22)

# 2.0a21

This release contains minor bug fixes to align with actual API response values for device personas.

### Bug Fixes

- **Device Persona Handling**
  - Corrected the persona key for Campus Access Points in `SUPPORTED_CONFIG_PERSONAS` from `"Campus AP"` to `"Campus Access Point"` to match the value returned by the Central API
  - Added a warning log when a device's `device_function` value is not a recognised persona (and is not `'-'`), rather than silently skipping `config_persona` assignment

Full Changelog: [v2.0a20...v2.0a21](https://github.com/aruba/pycentral/compare/v2.0a20...v2.0a21)

# 2.0a20

This release significantly expands the monitoring module coverage for APs, Gateways, and WLANs, adds 429 rate-limit retry handling, fixes streaming WebSocket client issues, and updates product branding across the SDK.

### New Features

- **Expanded AP Monitoring Module**
  - Added fleet-level retrieval methods: `get_all_radios`, `get_radios`, `get_all_bssids`, `get_bssids`, `get_all_swarms`, `get_swarms`, `get_swarm_details`
  - Added per-AP sub-resource methods: `get_ap_radios`, `get_ap_ports`, `get_all_ap_tunnels`, `get_ap_tunnels`, `get_ap_tunnel_details`, `get_ap_wlans`
  - Added trend endpoints: `get_ap_trends` (throughput, CPU, memory, power consumption), `get_ap_radio_trends` (throughput, channel utilization/quality, noise floor, frames), `get_ap_port_trends` (throughput, frames, CRC, collisions), `get_ap_tunnel_trends` (throughput, packet loss, MOS, jitter, latency)
- **Expanded Gateway Monitoring Module**
  - Added sub-resource methods: `get_all_gateway_ports`, `get_gateway_ports`, `get_gateway_port_details`, `get_all_gateway_vlans`, `get_gateway_vlans`, `get_gateway_vlan_details`, `get_all_gateway_tunnels`, `get_gateway_tunnels`, `get_gateway_tunnel_details`, `get_gateway_uplinks`, `get_gateway_uplink_details`, `get_all_gateway_dhcp_pools`, `get_gateway_dhcp_pools`, `get_all_gateway_dhcp_clients`, `get_gateway_dhcp_clients`
  - Added trend endpoints: `get_gateway_trends` (CPU, memory, WAN/VPN availability, hardware temperature), `get_gateway_port_trends` (throughput, frames, errors, packets), `get_gateway_tunnel_trends` (throughput, status, dropped packets), `get_gateway_uplink_trends` (throughput, WAN compression, WAN availability)
  - Added uplink probe methods: `get_gateway_uplink_probes`, `get_gateway_uplink_probe_performance_trends`, `get_gateway_uplink_vpn_availability_trends`
  - Added tunnel health: `get_gateway_tunnel_health_summary` (LAN/WAN)
  - Added cluster methods: `get_all_cluster_members`, `get_cluster_members`, `get_all_cluster_tunnels`, `get_cluster_tunnels`, `get_cluster_vlan_mismatch`, `get_cluster_connectivity_graph`, `get_cluster_tunnel_summary`, `get_cluster_capacity_trends`
- **WLAN Monitoring Module**
  - Added `WLAN` class with `get_all_wlans` and `get_wlans` methods supporting site_id, serial_number, filter, and sort parameters
- **429 Rate-Limit Retry**
  - `NewCentralBase.command()` now retries once after a 1-second pause when a 429 (Too Many Requests) response is received; logs an error and exits if the second attempt also fails

### Bug Fixes

- **Streaming WebSocket Client**
  - Event-type filters are now sent as URL query parameters instead of custom headers, fixing filter delivery to the server
  - Token refresh uses internal `_renew_token()` instead of deprecated `handle_expired_token()`
  - Cached `app_route` and `token_key` for correct internal lookups
  - Query parameters are stripped from connection log messages for readability

### Improvements

- **Shared Monitoring Utilities**
  - Added `get_all_pages` — generic pagination helper that replaces per-module while loops
  - Added `execute_trend_request` and `normalize_trend_response` — unified trend endpoint execution and response normalization
  - Added validation helpers: `validate_site_id`, `validate_query_length`, `validate_limit_and_next`, `validate_required_value`, `validate_serial_query`, `normalize_metric`, `build_trend_params`
  - Fixed `execute_get` default params (mutable default argument) and endpoint validation logic
  - Renamed `clean_switch_trend_data` → `_clean_switch_trend_data` (internal)
- **Constants Consolidation**
  - Extracted all pagination limits (AP_LIMIT, GATEWAY_LIMIT, SWITCH_LIMIT, etc.) into `pycentral/new_monitoring/constants.py`
- **Branding Update**
  - Shortened "HPE Aruba Networking Central" references to "Central" across documentation, docstrings, and project metadata
  - Updated project author to `hpe-networking-automation`
- Switches module refactored to use shared `get_all_pages`, `build_trend_params`, and validation utilities
- Updated monitoring API reference documentation with endpoint tables for APs, Gateways, and WLANs
- Fixed `next_cursor` type annotation in troubleshooting docstring (`int` → `int or str`)

Full Changelog: [v2.0a19...v2.0a20](https://github.com/aruba/pycentral/compare/v2.0a19...v2.0a20)

# 2.0a19

This release introduces MSP tenant connection management, a new Switches monitoring module, expanded troubleshooting event capabilities, ISO location validation for site creation, and refactored shared monitoring utilities.

### New Features

- **MSP Tenant Connection Support**
  - Added `MSPBase` class — a `NewCentralBase` subclass for Managed Service Provider workflows
  - `get_tenant_connection(tenant_name, tenant_workspace_id)` performs an RFC 8693 token exchange and returns an isolated `TenantBase` connection scoped to a specific tenant's Central environment
  - Tenant connections are cached internally; repeat calls with the same `tenant_workspace_id` return the same `TenantBase` instance without re-running the exchange
  - `close_tenant_connection(tenant_workspace_id)` closes a single cached tenant connection
  - `get_tenant_id(tenant_name)` resolves a tenant display name to its GLP workspace ID
  - Added `TenantBase` class that overrides `_renew_token()` to re-exchange the MSP parent token automatically when a tenant-scoped token expires
- **Switches Monitoring Module**
  - Added `MonitoringSwitches` class with the following methods:
    - `get_all_switches`, `get_switches` — paginated switch retrieval with filter and sort support
    - `get_switch_details` — fetch details for a specific switch by serial number
    - `get_stack_members` — retrieve stack members for a stacked switch
    - `get_switch_hardware_categories` — hardware category data for a switch
    - `get_switch_lag` — LAG (Link Aggregation Group) information
    - `get_switch_interfaces` — interface list with optional filtering and pagination
    - `get_switch_vlans` — VLAN membership data for a switch
    - `get_topn_interface_trends` — top-N interface utilization trends
    - `get_switch_interface_trends` — per-interface trend data over a time range
    - `get_switch_hardware_trends` — hardware utilization trends (CPU, memory, etc.)
    - `get_switch_interface_poe` — PoE usage data per interface
    - `get_switch_vsx` — VSX (Virtual Switching Extension) state for a switch
- **Troubleshooting Event Enhancements**
  - Added `list_event_filters` method to `Troubleshooting` and `Device` classes to retrieve available event filter options
  - Added `get_event_extra_attributes` method to fetch additional metadata fields for a specific event type
  - `list_events` now accepts an optional `duration` parameter for time-range based filtering
- **ISO Location Validation for Site Creation**
  - `Site.create_site()` now validates `country`, `state`, and `city` inputs against ISO 3166 standards via the new `validate_iso_location` utility before submitting the API request
  - Added `pycountry` dependency (`26.2.16`) to support ISO validation

### Improvements

- Extracted `validate_device_serial`, `validate_central_conn_and_serial`, `generate_timestamp_str`, and `clean_switch_trend_data` from per-module private helpers into shared `monitoring_utils` so APs, Gateways, and Switches all use the same validation path
- Added `_renew_token()` hook to `NewCentralBase` — subclasses can now override token renewal behavior without patching `command()`
- `LoginError` and `ValueError` are now re-raised directly from `command()` instead of being wrapped in `ResponseError`, making authentication failures easier to catch programmatically
- Improved error message when token creation does not return an `access_token`, providing clearer guidance on verifying client credentials and token URL
- HTTP client close failures are now logged at `ERROR` level instead of `DEBUG`
- Updated Switches monitoring documentation in `docs/modules/new_monitoring.md`
- Added full MSP module documentation in `docs/modules/msp.md`

Full Changelog: [v2.0a18...v2.0a19](https://github.com/aruba/pycentral/compare/v2.0a18...v2.0a19)

# 2.0a18

This release introduces unified credential support for GLP and New Central API calls, refines token initialization and refresh behavior, updates authentication guidance, and refreshes package requirements for the 2.0a18 release.

### New Features

- **Unified Credential Support**
  - Added a new `unified` credential model that allows one GLP credential set to be used for both GLP and New Central API calls
  - Unified mode uses GLP `client_id`, `client_secret`, and `workspace_id` to generate a single token and reuse it across supported platform requests
  - Supports GLP-only usage when no Central `base_url` or `cluster_name` is provided
  - When `unified` credentials are present, standalone `glp` and `new_central` entries are ignored in favor of the unified configuration

### Improvements

- Added support for the global OAuth token issuer flow used by unified credential management
- Refactored token parsing and route initialization to better support shared-token behavior across GLP and New Central
- Improved token creation and refresh error handling with clearer validation and more actionable failures for invalid credentials or incomplete configuration
- Updated authentication documentation with unified credential guidance, required fields, and example configurations
- Bumped package version references to `2.0a18`
- Updated package requirements in `pyproject.toml`, including Python version support and the pinned `requests` dependency

Full Changelog: [v2.0a17...v2.0a18](https://github.com/aruba/pycentral/compare/v2.0a17...v2.0a18)

# 2.0a17

This release introduces transient error retry with exponential backoff in the HTTP layer, refactors device attribute initialization, expands the known cluster URL registry, and updates getting-started documentation to clarify authentication prerequisites.

### New Features

- **Retry with Exponential Backoff**
  - `request_url` now automatically retries on transient transport failures (DNS errors, connection failures, timeouts, proxy errors) with exponential backoff up to 3 attempts
  - Added `RETRY_MAX_RETRIES`, `RETRY_INITIAL_BACKOFF`, `RETRY_BACKOFF_MULTIPLIER`, and `TRANSIENT_TRANSPORT_ERRORS` constants to `base.py`
  - All other exceptions are raised immediately as `ResponseError` without retrying
- **Unknown Base URL Warning**
  - `_resolve_base_url` now validates the resolved URL against known cluster URLs
  - Issues a non-fatal `UserWarning` if the URL is not a recognized Central cluster, expected for Central-On Prem & other non-production environments

### Improvements

- Added explicit `self.materialized = False` initialization at the top of `Device.__init__` for clarity
- `from_api` branch in `Device.__init__` now raises `ValueError` if `device_attributes` is `None`, preventing silent failures
- Replaced manual key-rename loop and `setattr` calls in `Device.__init__` with new `_apply_api_attributes()` helper method
- Device inventory fetch in `Device.get()` now uses `filter_str="serialNumber eq {serial}"` instead of the `search=` parameter to match updated API behavior
- Expanded `CLUSTER_BASE_URLS` in `constants.py` with changes to API Gateway Base URLs
- Removed unused `_return_client_credentials` method from `base.py`
- Updates to `Authentication` & `Quickstart` guide

Full Changelog: [v2.0a16...v2.0a17](https://github.com/aruba/pycentral/compare/v2.0a16...v2.0a17)

# 2.0a16

This release removes the deprecated search parameter from monitoring functions and updates the httpx dependency to the latest patch version.

### Improvements

- Removed search parameter from monitoring functions
  - `get_device_inventory()` and `get_all_device_inventory()` no longer accept `search` parameter as the underlying Central API no longer supports this filter
- Updated httpx dependency
  - Bumped httpx[http2] from 0.28.0 to 0.28.1 in pyproject.toml
- Changed default `log_level` from `"DEBUG"` to `"INFO"` in `NewCentralBase`
  - Reduces noise for users who do not explicitly configure logging
- README updated
  - Quickstart example now uses the context manager pattern (`with NewCentralBase(...) as conn`) to reflect current best practices
  - Updated documentation URLs

Full Changelog: [v2.0a15...v2.0a16](https://github.com/aruba/pycentral/compare/v2.0a15...v2.0a16)

# 2.0a15

This release migrates core monitoring modules to stable v1 APIs, replaces the HTTP client with HTTPX for persistent connection reuse, and introduces several bug fixes, stability improvements, and developer experience enhancements across the SDK.

### New Features

- HTTPX Migration
  - Replaced `requests.Session` with `httpx` for persistent connection reuse across API calls in `base.py`
  - Eliminates per-call connection overhead, significantly improving SDK performance
  - Supporting helper functions added to `base.py` to modularize command function internals
- v1 API Migration
  - Migrated modules of `MonitoringAPs`, `Clients`, `MonitoringDevices`, and `MonitoringSites` from Alpha/Beta APIs to stable v1 endpoints
  - Higher rate limits and expanded capabilities available for all migrated modules due to v1 API support
- Context Manager Support
  - `with` syntax now supported for SDK client instantiation
- Streaming: Ping-Pong Support
  - Added ping-pong capability to the streaming module to sustain longer-lived WebSocket connections
- Project Modernization
  - Migrated project initialization from `setup.py` to `pyproject.toml`

### Improvements

- Fixed duplicate `requests.Session` instantiation in Classic Central's `base.py`; session is now initialized once at startup and reused across API calls (Closes #65)
- Resolved bugs in log statements and return values within util modules - `scope_utils.py` & `monitoring_utils.py`
- Abstracted valid personas into a dedicated structure for easier maintenance in `constants.py`
- Added extra validation checks across scope-related helper functions in `scope_base.py` & `scopemaps.py`
- Updated URL utils to default to v1 endpoints unless explicitly overridden
- Documentation updates for all above changes

Full Changelog: [v2.0a14...v2.0a15](https://github.com/aruba/pycentral/compare/v2.0a14...v2.0a15)

# 2.0a14

This release improves profile retrieval reliability, refines the show commands interface to support increased input handling, and extends client management functionality with new helper utilities and dependency updates.

### Improvements

- Updated `get_profile` docstring and added handling for invalid URL responses to improve robustness during profile lookups
- Updated show command methods across Troubleshooting & Device classes to reflect API changes. Related functions now accept either a string or a list of strings representing the set of show commands to be run on the devices
- Updated dependencies: `requests==2.32.5`, `PyYAML==6.0.3`, `protobuf==6.33.5` to ensure compatibility and stability
- Added `get_client_details` method to fetch client-specific details
- Added `_validate_mac_address` helper method to support input validation for MAC address fields

Full Changelog: [v2.0a13...v2.0a14](https://github.com/aruba/pycentral/compare/v2.0a13...v2.0a14)

# 2.0a13

This release expands monitoring and troubleshooting capabilities and introduces SDK-level support for Streaming APIs, enabling developers to consume supported WebSocket-based event streams using a native client and decoders.

### New Features

- Monitoring Enhancements
  - Added new methods under `MonitoringAPIs`:
    - `get_wlans`
    - `get_ap_wlans`
  - These methods allow users to retrieve WLAN data associated with a specific AP or across all APs, aligning with the underlying monitoring API implementations
- Troubleshooting Events Support
  - Added support for troubleshooting events via the new `list_events` method. This method enables retrieval of network events using query-based filtering
  - Implemented method across `Troubleshooting` and `Device` classes to provide consistent access patterns
- Streaming APIs Support
  - Added SDK support for consuming Streaming APIs with a built-in streaming client that handles connection management and event decoding
  - Introduced streaming topic decoders with support for the following event types:
    - Audit Trail
    - Location
    - Location Analytics
    - Geofence
  - Added accompanying documentation to guide users on streaming setup, topic usage, and event decoding

### Improvements

- Fixed minor bugs and applied cleanup across methods in `scope_utils.py`
- Improved stability and consistency of scope-related helper functions, including `get_all_scope_elements`

Full Changelog: [v2.0a12...v2.0a13](https://github.com/aruba/pycentral/compare/v2.0a12...v2.0a13)

# 2.0a12

This release focuses on expanding troubleshooting capabilities and improving how the SDK documents and exposes its public methods.

### New Features

- Added new troubleshooting modules that expose additional troubleshooting methods - `list_show_commands`, `list_active_tasks`, `run_show_command`, `initiate_show_command`, `get_show_command_result`
- Introduced troubleshooting helpers in the `Devices` class to support new methods mentioned above

### Updates

- Migrated docstrings from Sphinx style to Google style across core modules (e.g. `Devices`, `Monitoring`, `Troubleshooting`, `Sites`, `Profiles`, and related utilities)
  - Standardized parameter/return/exception sections for better readability and IDE support
  - Added missing docstrings for existing public methods to keep behavior and usage clearly documented
- Removed legacy Sphinx documentation files that are no longer used by the current docs pipeline
- Removed unused custom exceptions such as `UnsupportedCapabilityError` & `GenericOperationError`
- Replaced direct `exit` calls with raised exceptions so error handling is consistent and easier for applications to manage

### Improvements

- Removed duplicate endpoint implementations in the `Devices` class where equivalent functionality already exists in the Monitoring modules; `Devices` now reuses the Monitoring implementations instead of maintaining separate copies
- Improved overall error-handling to align with the new exception model

Full Changelog: [v2.0a11...v2.0a12](https://github.com/aruba/pycentral/compare/v2.0a11...v2.0a12)

# 2.0a11

1. Updated logic of device function to persona mapping to match API behaviour
2. Updates to documentation for certain functions
3. Resolved minor issues of GLP Subscriptions module

Full Changelog: [v2.0a10...v2.0a11](https://github.com/aruba/pycentral/compare/v2.0a10...v2.0a11)

# 2.0a10

This update introduces new Monitoring modules that simplify how users access site/device/client metrics, while also removing deprecated profiles and improving URL generation for a cleaner and more efficient SDK usage experience.

### New Features

This release introduces new Monitoring modules that expose Monitoring API capabilities across Sites, Devices, Access Points, Gateways, and Clients.
These modules provide direct methods for common monitoring tasks, eliminating the need to manually call endpoints, handle pagination, or build aggregation logic.

Monitoring Modules Added:
- Sites: `get_all_sites`, `get_sites`, `get_site_device_health`, `list_site_information`
- Devices: `get_all_devices`, `get_devices`, `get_device_inventory`, `delete_device`
- Access Points: `get_all_aps`, `get_aps`, `get_latest_ap_stats`, `get_ap_cpu_utilization`, `get_ap_memory_utilization`, `get_ap_poe_utilization`
- Gateways: `get_all_gateways`, `get_gateways`, `get_cluster_leader_details`, `get_gateway_details`, `get_gateway_interfaces`, `get_gateway_lan_tunnels`, `get_stats`, `get_latest_gateway_stats`, `get_gateway_cpu_utilization`, `get_gateway_memory_utilization`, `get_gateway_wan_availability`, `get_tunnel_health_summary`
- Clients: `get_all_site_clients`, `get_wireless_clients`, `get_wired_clients`, `get_clients_associated_device`, `get_connected_clients`, `get_disconnected_clients`, `get_site_clients`, `get_client_trends`, `get_top_n_site_clients`

### Updates

- Removed deprecated modules and related dead code - `Policy`, `Role`, `SystemInfo`, `Vlan`, `Wlan`
  - Please use `Profiles` class instead of the above modules
- Improved Profiles documentation and overall code quality of module methods

### Improvements

- Introduced new `generate_url` function to simplify URL generation and parameter handling
- Split category mappings and API endpoints into dedicated files for cleaner import flows
- Replaced all legacy `fetch_url` and `generate_url_with_params` usage
- Removed unused `NewCentralURLs` imports

Full Changelog: [v2.0a9...v2.0a10](https://github.com/aruba/pycentral/compare/v2.0a9...v2.0a10)

# 2.0a9

This update primarily extends the Troubleshooting module with new methods, and introduces supporting documentation. It also reorganizes the Troubleshooting class for improved efficiency and readability, while ensuring the Device class supports all new troubleshooting methods.

### New Features

- Troubleshooting Class
  - Added support for new methods:
    - AAA test implementation for Access Points (APs)
    - NSLOOKUP test for APs
    - User disconnect functions for APs
    - Client disconnect functions for Gateways
  - Added a `troubleshooting.md` file that documents all supported troubleshooting test in the SDK, including corresponding methods along with supported device types
- Device Class
  - Added support for all newly introduced troubleshooting methods
- Scopes Module
  - Added `find_device_group` method

### Updates

- Troubleshooting Class
  - Replaced `ping_test` method with `ping_aps_test`, `ping_cx_test`, `ping_aoss_test`, `ping_gateways_test` to align with device-type-specific troubleshooting attributes
  - Replaced `traceroute_test` method with `traceroute_aps_test`, `traceroute_cx_test`, `traceroute_aoss_test`, `traceroute_gateways_test` to align with device-type-specific troubleshooting attributes

### Improvements

- Troubleshooting Class
  - Reorganized Troubleshooting class for efficiency, readability, and easier future maintenance
  - Removed redundant checks on troubleshooting test attributes

Full Changelog: [v2.0a8...v2.0a9](https://github.com/aruba/pycentral/compare/v2.0a8...v2.0a9)

# 2.0a8

This update adds a dedicated Troubleshooting class with new diagnostic methods across multiple device types, enhances the Device class, and includes key dependency updates and cleanup.

### New Features

- `Troubleshooting` Class - Added support for Access Points, AOS-CX, AOS-S, and Gateways
  - New troubleshooting methods - Ping, Traceroute, Reboot, Locate, HTTP/HTTPS Tests, Port Bounce, PoE Bounce, ARP Table, Speedtest, AAA Test, Cable Test, and Iperf Test
- `Device` Class - Now supports all troubleshooting methods

### Updates

- Updated dependencies:
  - `requests`: 2.32.3 -> 2.32.4
  - `pytz`: 2024.1 -> 2025.2
- Removed unused dependencies: `urllib3`, `certifi`, `termcolor`

### Improvements

- Removed minimum site collection requirement for fetching global ID and profile correlation in scopes
- Enhanced error logging for scope initialization without a site

Full Changelog: [v2.0a7...v2.0a8](https://github.com/aruba/pycentral/compare/v2.0a7...v2.0a8)

# 2.0a7

This update introduces support for Device_Group in Scopes, improves persona assignment workflows, and fixes key bugs related to scope correlation and device identification.

### New Features

- Device Group Class - Introduced `Device_Group` class for use in Scopes & integrated into `ScopeBase` to ensure consistency with other scope types
- Scope Class Enhancements
  - Added `type` attribute to all scope-related classes: `Scopes`, `Site`, `Site_Collection`, `Device`, `Device_Group`
  - Improved `get_all_devices` method in the `Device` class:
    - Method uses `isProvisioned` to filter devices configured via the new Central
- Profile Persona
  - Added support for configuration persona for devices based on their function. This simplifies profile management for devices
  - `assign_profile`, `unassign_profile` methods now accept `profile_persona` as an optional parameter for devices
  - Added `SUPPORTED_CONFIG_PERSONAS` to `constants.py` for better maintainability

### Bug Fixes

- Fixed `_correlate_scopes` to ensure accurate correlation logic in `Scopes` class
- Improved logging in `_find_scope_element` method to clarify unknown scope errors in `Scopes` class
- Updated `rename_keys` in `Device` class to update device IDs as `int` instead of `string` for consistency with other IDs

Full Changelog: [v2.0a6...v2.0a7](https://github.com/aruba/pycentral/compare/v2.0a6...v2.0a7)

# 2.0a6

- Added Scope modules -
  - ScopeBase
  - Scope (Managing scope & Global)
  - Site Collection - CRUD Operations
  - Site - CRUD Operations
  - Device
  - Other scope management modules
- Added Config Profile modules -
  - Profile base
  - Policy
  - Role
  - System Info
  - VLAN
  - WLAN
- Enhancements to base module to support `enable_scope` attribute
  - This will fetch scope hierarchy related data to simplify automation scripting with SDK

Full Changelog: [v2.0a5...v2.0a6](https://github.com/aruba/pycentral/compare/v2.0a5...v2.0a6)

# 2.0a5

- Fixed bugs with `get_all_devices` and `get_all_subscriptions` in `Device` & `Subscriptions` modules
- Documentation updates for `Devices` & `Subscriptions` module
- Added `ServiceManager` GLP module

Full Changelog: [v2.0a3...v2.0a5](https://github.com/aruba/pycentral/compare/v2.0a3...v2.0a5)

# 2.0a3

- Token management support for New Central & GreenLake (GLP) API calls
- Backwards compatibility with Classic Central API calls & PyCentral-v1
- Added ability to make API calls to New Central & GLP via base module
- Introduced GLP modules for managing Devices, Subscriptions, & Users
- Enabled token reuse by storing generated tokens in provided token file (YAML/JSON)
- Added support for optionally providing `cluster_name` instead of `base_url` for New Central token information

Full Changelog: [v1.4.1...v2.0a3](https://github.com/aruba/pycentral/compare/v1.4.1...v2.0a3)

# 1.4.1

## Notable Changes
* Support Preserve Configuration Overrides in Device Movement by @fiveghz in #43
* Version fixes by @KarthikSKumar98 in #45
* Packages that are installed along with PyCentral will have version number associated with.
  * requests - v2.31.0
  * PyYAML - v6.0.1
  * urllib3 - 2.2.2
  * certifi - 2024.7.4
## New Contributors
* @fiveghz made their first contribution in [#43](https://github.com/aruba/pycentral/pull/43)
  
Full Changelog: [v1.4...v1.4.1](https://github.com/aruba/pycentral/compare/v1.4...v1.4.1)
## Known Issues
* No known issues.





# 1.4

## Notable Changes
* Updated minimum required version of python from 3.6 to 3.8
* Add the ability to consume cluster_name as a parameter instead of base_url
* Added ability to enable and disable WLANs in Central UI Group
  * enable_wlan
  * disable_wlan
* Error handling when invalid base_url is passed
* Resolved minor bugs
  
## Known Issues
* No known issues.

Full Changelog: [v1.3...v1.4](https://github.com/aruba/pycentral/compare/v1.3...v1.4)

# 1.3

## Notable Changes
* Added MSP Module. These are some of the functions that are implemented in this module -
  *  Customer Management Functions
     *  get_customers
     *  get_all_customers
     *  create_customer
     *  update_customer
     *  delete_customer
     *  get_customer_details
     *  get_customer_id
  *  Device Management Functions
     *  get_customer_devices_and_subscriptions
     *  assign_devices_to_customers
     *  unassign_devices_from_customers
     *  unassign_all_customer_device
     *  get_msp_devices_and_subscriptions
     *  get_msp_all_devices_and_subscriptions
  *  Other Functions
     *  get_msp_id
     *  get_msp_users
     *  get_customer_users
     *  get_country_code
     *  get_country_codes_list
     *  get_msp_resources
     *  edit_msp_resources
     *  get_customers_per_group

Full Changelog: [v1.2.1...v1.3](https://github.com/aruba/pycentral/compare/v1.2.1...v1.3)

## Known Issues
* No known issues.

# 1.2.1

## Notable Changes
* Fixed bug with add_device function

## Known Issues
* No known issues.

# 1.2

## Notable Changes
* Added new Device Inventory functions - Archive Devices, Unarchive Devices, Add Devices

## Known Issues
* No known issues.

## PRs in this release
* Added device inventory functions by [@KarthikSKumar98](https://github.com/KarthikSKumar98) in [#35](https://github.com/aruba/pycentral/pull/35)
* Style linting pycentral modules by[@KarthikSKumar98](https://github.com/KarthikSKumar98) in [#36](https://github.com/aruba/pycentral/pull/36)

Full Changelog: [v1.1.1...v1.2](https://github.com/aruba/pycentral/compare/v1.1.1...v1.2)

# 1.1.1

## Notable Changes
* Updated README links

## Known Issues
* No known issues.
  
# 1.1.0

## Notable Changes
* Added APConfiguration Class to Configuration Module

## Known Issues
* No known issues.
  
# 1.0.0

## Notable Changes
* Added wait & retry logic when Aruba Central's Per-Second API rate-limit is hit
* Added log messages when Aruba Central's Per-Day API Rate-limit is exhausted
* Added new module for device_inventory APIs
* Added WLAN class to configuration module
* Merged PRs and resolved GitHub issues:
    - PR #16 : Fixing multiple devices to site bug
    - PR #19 : Added ability to associate/unassociate multiple devices to a site
    - PR #20 : Added New Device Inventory Module
    - PR #22 : Added Rate Limit Log Messages
    - PR #23 : Fixed Rate Limit Bugs
    - PR #25 : Licensing API Bug Fixes
    - PR #28, #29 : Added WLAN class to Configuration module

## Known Issues
* No known issues.
  
# 0.0.3

## Notable Changes
* Quick fix on deprecated pip module usage.
* Merged PRs and resolved GitHub issues:
    - PR #10 : remove dep on _internal function from pip module 
    - Issue #9: pip 21.3 just posted 2 days ago breaks pycentral in the config file and passed to pycentral

## Known Issues
* No known issues.
  
# 0.0.2

## Notable Changes
* Added modules for firmware_management, rapids, topology and user_management
* Major update to existing config_apsettings_from_csv.py workflow. It accepts CSV file downloaded from the Central UI group. This workflow also generates a new CSV file with failed APs. CSV file format from the previous version is not backward compatible.
* Fixes and improvement to existing modules, utilities and the documentation
* Merged PRs and resolved GitHub issues:
    - PR #6: example AP rename code always terminates with an error
    - PR #2: fix url concat in command()
    - PR #1: Added the ability for multiple Aruba Central account's in the config file and passed to pycentral

## Known Issues
* No known issues.

# 0.0.1

## Notable Changes
* This is the initial release for the Aruba Central Python SDK, sample scripts, and workflows.

## Known Issues
* No known issues.
