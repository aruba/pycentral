# API Coverage Expansion Plan

This document tracks the plan to implement all unimplemented New Central and New Central Config API
endpoints in pycentral. Each phase is ordered by user impact.

All PRs implementing items from this plan must:
- Reference a GitHub issue number
- Target `v2(pre-release)` branch
- Include DCO sign-off (`git commit -s`)
- Follow PEP-8 with reStructuredText docstrings

---

## Prerequisite: `url_utils.py` updates

Before or alongside Phase 1, `pycentral/utils/url_utils.py` needs two changes:

1. **New categories** — add to the `CATEGORIES` dict:
   ```python
   "notifications": {
       "value": "network-notifications",
       "type": "monitoring",
       "latest": "v1",
   },
   "services": {
       "value": "network-services",
       "type": "monitoring",
       "latest": "v1",
   },
   "nac": {
       "value": "nac-service",
       "type": "configuration",
       "latest": "v1",
   },
   ```

2. **Version list** — the `versions` list only contains `["v1alpha1", "v1"]`, but several endpoints
   use `v1alpha2` (e.g. gateway monitoring). Add `"v1alpha2"` to the list.

---

## Phase 1 — High-impact gaps (Monitoring & Services)

### 1.1 Switch Monitoring — new file `pycentral/new_monitoring/switches.py`

New class: `MonitoringSwitches`

| Method | HTTP | Endpoint |
|---|---|---|
| `get_switches` | GET | `network-monitoring/v1/switches` |
| `get_all_switches` | — | pagination wrapper around `get_switches` |
| `get_switch_details` | GET | `network-monitoring/v1/switches/{serial_number}` |
| `get_switch_ports` | GET | `network-monitoring/v1/switches/{serial_number}/ports` |
| `get_switch_port_details` | GET | `network-monitoring/v1/switches/{serial_number}/ports/{port_id}` |
| `get_switch_port_throughput` | GET | `network-monitoring/v1/switches/{serial_number}/ports/{port_id}/throughput-trends` |
| `get_switch_cpu_utilization` | GET | `network-monitoring/v1/switches/{serial_number}/cpu-utilization-trends` |
| `get_switch_memory_utilization` | GET | `network-monitoring/v1/switches/{serial_number}/memory-utilization-trends` |
| `get_switch_stats` | — | parallel wrapper (cpu + memory) mirroring `MonitoringAPs.get_ap_stats` |
| `get_switch_stacks` | GET | `network-monitoring/v1/switch-stacks` |
| `get_switch_stack_details` | GET | `network-monitoring/v1/switch-stacks/{stack_id}` |
| `get_switch_vlans` | GET | `network-monitoring/v1/switches/{serial_number}/vlans` |

Verify exact paths and all query parameters from the API reference before implementing:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/getswitchesv1?json=on" \
  | jq '.oasDefinition.paths'
```

### 1.2 Alerts / Notifications — new file `pycentral/new_monitoring/alerts.py`

New class: `Alerts`

Uses `category="notifications"` (new category defined in prerequisite above).

| Method | HTTP | Endpoint |
|---|---|---|
| `get_alerts` | GET | `network-notifications/v1/alerts` |
| `get_all_alerts` | — | pagination wrapper around `get_alerts` |

Verify from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/getalertlistv1?json=on" \
  | jq '.oasDefinition.paths'
```

### 1.3 Webhooks — new file `pycentral/services/webhooks.py`

New package `pycentral/services/` with `__init__.py`. New class: `Webhooks`

Uses `category="services"` (new category defined in prerequisite above).

| Method | HTTP | Endpoint |
|---|---|---|
| `get_webhooks` | GET | `network-services/v1/webhooks` |
| `create_webhook` | POST | `network-services/v1/webhooks` |
| `get_webhook` | GET | `network-services/v1/webhooks/{webhook_id}` |
| `update_webhook` | PUT | `network-services/v1/webhooks/{webhook_id}` |
| `patch_webhook` | PATCH | `network-services/v1/webhooks/{webhook_id}` |
| `delete_webhook` | DELETE | `network-services/v1/webhooks/{webhook_id}` |
| `rotate_hmac_key` | POST | `network-services/v1/webhooks/{webhook_id}/hmac-key` |

Verify from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/getwebhooksv1?json=on" \
  | jq '.oasDefinition'
```

### 1.4 Device Group Write Operations — extend `pycentral/scopes/`

Currently `Device_Group` is read-only and `Device_Group.__init__` raises if `from_api=False`.

Add a standalone `DeviceGroupAPI` class (or functions module) in `pycentral/scopes/device_group_api.py`:

| Method | HTTP | Endpoint |
|---|---|---|
| `get_device_groups` | GET | `network-config/v1alpha1/device-collections` |
| `create_device_group` | POST | `network-config/v1alpha1/device-collections` |
| `update_device_group` | PUT | `network-config/v1alpha1/device-collections/{scope_id}` |
| `delete_device_group` | DELETE | `network-config/v1alpha1/device-collections/{scope_id}` |
| `delete_device_groups_bulk` | DELETE | `network-config/v1alpha1/device-collections` (bulk) |
| `add_devices` | POST | `network-config/v1alpha1/device-collections/{scope_id}/devices` |
| `remove_devices` | DELETE | `network-config/v1alpha1/device-collections/{scope_id}/devices` |

Verify from:
```bash
curl -s "https://developer.arubanetworks.com/new-central-config/reference/getdevicegroupsv1?json=on" \
  | jq '.oasDefinition.paths'
```

---

## Phase 2 — Services & Supporting Monitoring

### 2.1 Firmware Details — `pycentral/services/firmware.py`

New class: `FirmwareService`. Uses `category="services"`.

| Method | HTTP | Endpoint |
|---|---|---|
| `get_firmware_details` | GET | `network-services/v1/firmware-details` |

Verify from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/getfirmwaredetailslistv1?json=on" \
  | jq '.oasDefinition.paths'
```

### 2.2 Audit Trail — `pycentral/services/audit.py`

New class: `AuditTrail`. Uses `category="services"`.

| Method | HTTP | Endpoint |
|---|---|---|
| `get_audit_events` | GET | `network-services/v1/audit` |
| `get_audit_event_details` | GET | `network-services/v1/audit/{event_id}` |

Verify from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/get_audit_resp_info?json=on" \
  | jq '.oasDefinition.paths'
```

### 2.3 Reporting — `pycentral/new_monitoring/reporting.py`

New class: `Reporting`.

| Method | HTTP | Endpoint |
|---|---|---|
| `list_reports` | GET | `network-monitoring/v1alpha1/reports` |
| `create_report` | POST | `network-monitoring/v1alpha1/reports` |
| `get_report` | GET | `network-monitoring/v1alpha1/reports/{report_id}` |
| `update_report` | PUT | `network-monitoring/v1alpha1/reports/{report_id}` |
| `delete_report` | DELETE | `network-monitoring/v1alpha1/reports/{report_id}` |
| `list_report_runs` | GET | `network-monitoring/v1alpha1/reports/{report_id}/runs` |

Verify from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/listreports?json=on" \
  | jq '.oasDefinition.paths'
```

### 2.4 Location Services — `pycentral/new_monitoring/location.py`

New class: `LocationServices`.

| Method | HTTP | Endpoint |
|---|---|---|
| `get_device_locations` | GET | `network-monitoring/v1alpha2/device-locations` |
| `get_location_by_id` | GET | `network-monitoring/v1alpha2/locations/{location_id}` |
| `get_device_detailed_location` | GET | `network-monitoring/v1alpha2/devices/{serial_number}/location` |
| `get_ap_ranging_scans` | GET | `network-monitoring/v1alpha2/aps/{serial_number}/ranging-scans` |
| `get_ap_ranging_scan` | GET | `network-monitoring/v1alpha2/aps/{serial_number}/ranging-scans/{scan_id}` |
| `list_asset_tag_data` | GET | `network-monitoring/v1alpha2/asset-tags` |

Verify all paths and versions from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/getdevicelocationsv1alpha2?json=on" \
  | jq '.oasDefinition.paths'
```

### 2.5 Location Analytics — `pycentral/new_monitoring/location_analytics.py`

New class: `LocationAnalytics`.

| Method | HTTP | Endpoint |
|---|---|---|
| `get_trends` | GET | `network-monitoring/v1/location-analytics/trends` |
| `get_site_insights` | GET | `network-monitoring/v1/location-analytics/sites/{site_id}/insights` |

Verify from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/getlatrendsforapiv1?json=on" \
  | jq '.oasDefinition.paths'
```

---

## Phase 3 — Troubleshooting Expansion

The existing `pycentral/troubleshooting/troubleshooting.py` only covers the events endpoint. Extend it
(or add sub-modules) with the following. Verify all paths and request schemas before implementing —
the troubleshooting API is the most complex in terms of request bodies.

### 3.1 AP Troubleshooting

| Method | HTTP | Endpoint |
|---|---|---|
| `ap_ping` | POST | `network-troubleshooting/v1alpha1/aps/{serial_number}/ping` |
| `ap_traceroute` | POST | `network-troubleshooting/v1alpha1/aps/{serial_number}/traceroute` |
| `ap_speedtest` | POST | `network-troubleshooting/v1alpha1/aps/{serial_number}/speedtest` |
| `ap_show_command` | POST | `network-troubleshooting/v1alpha1/aps/{serial_number}/show-command` |
| `ap_reboot` | POST | `network-troubleshooting/v1alpha1/aps/{serial_number}/reboot` |
| `ap_locate` | POST | `network-troubleshooting/v1alpha1/aps/{serial_number}/locate` |
| `ap_disconnect_users` | POST | `network-troubleshooting/v1alpha1/aps/{serial_number}/disconnect-users` |
| `get_task_status` | GET | `network-troubleshooting/v1alpha1/tasks/{task_id}` |

### 3.2 Switch Troubleshooting (AOS-CX)

| Method | HTTP | Endpoint |
|---|---|---|
| `switch_ping` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/ping` |
| `switch_traceroute` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/traceroute` |
| `switch_poe_bounce` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/poe-bounce` |
| `switch_port_bounce` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/port-bounce` |
| `switch_cable_test` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/cable-test` |
| `switch_show_command` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/show-command` |
| `switch_reboot` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/reboot` |
| `switch_locate` | POST | `network-troubleshooting/v1alpha1/switches/{serial_number}/locate` |

### 3.3 Gateway Troubleshooting

| Method | HTTP | Endpoint |
|---|---|---|
| `gateway_ping` | POST | `network-troubleshooting/v1alpha1/gateways/{serial_number}/ping` |
| `gateway_traceroute` | POST | `network-troubleshooting/v1alpha1/gateways/{serial_number}/traceroute` |
| `gateway_iperf` | POST | `network-troubleshooting/v1alpha1/gateways/{serial_number}/iperf` |
| `gateway_show_command` | POST | `network-troubleshooting/v1alpha1/gateways/{serial_number}/show-command` |
| `gateway_reboot` | POST | `network-troubleshooting/v1alpha1/gateways/{serial_number}/reboot` |
| `gateway_disconnect_clients` | POST | `network-troubleshooting/v1alpha1/gateways/{serial_number}/disconnect-clients` |

Verify all troubleshooting endpoint paths and body schemas:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/appping?json=on" \
  | jq '.oasDefinition'
```

---

## Phase 4 — FloorPlan Management

New file: `pycentral/new_monitoring/floorplan.py`. New class: `FloorPlan`.
This is a large surface area — implement in sub-groups.

### 4.1 Floors & Buildings

| Method | HTTP | Endpoint |
|---|---|---|
| `get_buildings` | GET | `network-monitoring/v1/buildings` |
| `create_floor` | POST | `network-monitoring/v1/floors` |
| `get_floor_summary` | GET | `network-monitoring/v1/floors/{floor_id}` |
| `update_floor_map` | PUT | `network-monitoring/v1/floors/{floor_id}/map` |
| `delete_floor` | DELETE | `network-monitoring/v1/floors/{floor_id}` |
| `get_floor_map_image` | GET | `network-monitoring/v1/floors/{floor_id}/image` |
| `replace_floor_image` | PUT | `network-monitoring/v1/floors/{floor_id}/image` |
| `scale_floor_map` | POST | `network-monitoring/v1/floors/{floor_id}/scale` |
| `import_floors` | POST | `network-monitoring/v1/floors/import` |
| `get_import_status` | GET | `network-monitoring/v1/floors/import/{job_id}` |

### 4.2 Walls & Zones

| Method | HTTP | Endpoint |
|---|---|---|
| `get_wall_types` | GET | `network-monitoring/v1/wall-types` |
| `create_wall_types` | POST | `network-monitoring/v1/wall-types` |
| `update_wall_types` | PUT | `network-monitoring/v1/wall-types/{type_id}` |
| `delete_wall_types` | DELETE | `network-monitoring/v1/wall-types/{type_id}` |
| `get_walls` | GET | `network-monitoring/v1/floors/{floor_id}/walls` |
| `create_walls` | POST | `network-monitoring/v1/floors/{floor_id}/walls` |
| `update_walls` | PUT | `network-monitoring/v1/floors/{floor_id}/walls/{wall_id}` |
| `delete_walls` | DELETE | `network-monitoring/v1/floors/{floor_id}/walls/{wall_id}` |
| `get_zones` | GET | `network-monitoring/v1/floors/{floor_id}/zones` |
| `create_zones` | POST | `network-monitoring/v1/floors/{floor_id}/zones` |
| `update_zones` | PUT | `network-monitoring/v1/floors/{floor_id}/zones/{zone_id}` |
| `delete_zones` | DELETE | `network-monitoring/v1/floors/{floor_id}/zones/{zone_id}` |

### 4.3 Device Placement

| Method | HTTP | Endpoint |
|---|---|---|
| `get_placed_devices` | GET | `network-monitoring/v1/floors/{floor_id}/devices` |
| `place_devices` | POST | `network-monitoring/v1/floors/{floor_id}/devices` |
| `remove_devices` | DELETE | `network-monitoring/v1/floors/{floor_id}/devices` |
| `change_device_assignment` | PATCH | `network-monitoring/v1/floors/{floor_id}/devices/{device_id}` |
| `get_associated_devices` | GET | `network-monitoring/v1/floors/{floor_id}/associated-devices` |
| `get_heatmap` | GET | `network-monitoring/v1/floors/{floor_id}/heatmap` |
| `get_channel_occupancy_heatmap` | GET | `network-monitoring/v1/floors/{floor_id}/channel-occupancy-heatmap` |

Verify all FloorPlan paths from:
```bash
curl -s "https://developer.arubanetworks.com/new-central/reference/getsummaryv1?json=on" \
  | jq '.oasDefinition.paths'
```

---

## Phase 5 — Configuration Profiles (Config API)

The generic `Profiles` class in `pycentral/profiles/profiles.py` can already call any
`network-config/v1alpha1/` path if you know the endpoint slug. Phase 5 is about adding
**typed, documented wrapper classes** for the major profile categories so callers don't
need to know the raw paths.

Each wrapper should follow this pattern (see `profiles.py` for the base implementation):
- Accept a `central_conn` and the profile-specific fields
- Delegate CRUD to `Profiles.create_profile` / `get_profile` / `update_profile` / `delete_profile`
- Document all fields and constraints from the OpenAPI spec

### 5.1 Interface Profiles — new file `pycentral/config/interfaces.py`

Typed wrappers for: Ethernet Interface, VLAN Interface, Port Channel, LACP, Loopback,
Sub-interfaces, LLDP, CDP, Switch Port Profile, AP Port Profile, sFlow, UFD, Management Interface.

Verify paths from:
```bash
curl -s "https://developer.arubanetworks.com/new-central-config/reference/readethernetinterfacebyid?json=on" \
  | jq '.oasDefinition.paths'
```

### 5.2 Routing & Overlay Profiles — new file `pycentral/config/routing.py`

Typed wrappers for: Static Route, OSPFv2, OSPFv3, BGP, VRF, Route Map, Prefix List,
AS-Path List, Community List, BFD, PIM, EVPN, Multicast, MSDP, MGMD, Track Object.

### 5.3 Security Profiles — new file `pycentral/config/security.py`

Typed wrappers for: AAA Profile, Auth Server, Auth Server Group, AAA Dot1x Auth/Supplicant,
AAA MAC Auth, AAA Captive Portal, Firewall, Certificates, MACsec, MACSec MKA, Port Security,
CoPP, UBT, Auth Survivability.

### 5.4 Network Service Profiles — new file `pycentral/config/network_services.py`

Typed wrappers for: DHCP Server, DHCP Pool, DHCP Relay, DHCP Snooping, QoS Global/Queue/Schedule,
Dynamic ARP Inspection, IP Lockdown, ND Snooping, UDP Broadcast Forwarder, NAE Lite, MGMD.

### 5.5 Roles & Policy Profiles — new file `pycentral/config/policy.py`

Typed wrappers for: Role, Policy, Object Group, Policy Group, Role ACL, Role GPID, Net Group.

### 5.6 Named Objects — new file `pycentral/config/named_objects.py`

Typed wrappers for: Network Service Object, Alias.

### 5.7 Other Config Profiles

- Firmware Compliance — `pycentral/config/firmware_policy.py`
- Gateway Clustering / HA — `pycentral/config/gateway_clustering.py`
- Overlay WLAN — `pycentral/config/overlay_wlan.py`
- Application Recognition Control (ARC) — `pycentral/config/arc.py`
- Config Checkpoint — `pycentral/config/checkpoints.py`
- Config Health — add to existing monitoring or new `pycentral/config/health.py`
  - `GET network-config/v1alpha1/active-issues`
  - `GET network-config/v1alpha1/config-health-devices`

New `pycentral/config/` package requires a `__init__.py`.

---

## Phase 6 — Central NAC Service

New package: `pycentral/nac/` with `__init__.py`. New categories needed in `url_utils.py`:
verify the correct base URL prefix from:
```bash
curl -s "https://developer.arubanetworks.com/new-central-config/reference/getmacregistrations?json=on" \
  | jq '.oasDefinition.servers'
```

### 6.1 MAC Registration — `pycentral/nac/mac_registration.py`

| Method | HTTP | Notes |
|---|---|---|
| `get_mac_registrations` | GET | |
| `create_mac_registration` | POST | |
| `update_mac_registration` | PUT | |
| `delete_mac_registration` | DELETE | |
| `export_mac_csv` | GET | streams CSV file |
| `import_mac_csv` | POST | multipart upload |

### 6.2 Named MPSK — `pycentral/nac/mpsk.py`

| Method | HTTP | Notes |
|---|---|---|
| `get_named_mpsk` | GET | |
| `create_named_mpsk` | POST | |
| `update_named_mpsk` | PUT | |
| `delete_named_mpsk` | DELETE | |
| `export_mpsk_csv` | GET | streams CSV |
| `import_mpsk_csv` | POST | multipart upload |

### 6.3 Visitor Management — `pycentral/nac/visitors.py`

| Method | HTTP | Notes |
|---|---|---|
| `get_visitors` | GET | |
| `create_visitor` | POST | |
| `update_visitor` | PUT | |
| `delete_visitor` | DELETE | |
| `export_visitor_csv` | GET | streams CSV |

### 6.4 DPP Registration — `pycentral/nac/dpp.py`

| Method | HTTP | Notes |
|---|---|---|
| `list_dpp_registrations` | GET | |
| `create_dpp_registration` | POST | |
| `update_dpp_registration` | PUT | |
| `get_dpp_registration` | GET | |
| `delete_dpp_registration` | DELETE | |

### 6.5 Certificates — `pycentral/nac/certificates.py`

| Method | HTTP | Notes |
|---|---|---|
| `list_certificates` | GET | |
| `revoke_certificates` | POST | |

### 6.6 NAC Jobs — `pycentral/nac/jobs.py`

| Method | HTTP | Notes |
|---|---|---|
| `list_jobs` | GET | |
| `get_job` | GET | |
| `delete_job` | DELETE | |
| `download_result_file` | GET | streamed |
| `download_error_file` | GET | streamed |
| `download_input_file` | GET | streamed |

---

## Implementation Notes

### Adding a new monitoring module

1. Create `pycentral/new_monitoring/<name>.py`
2. Import `execute_get` from `..utils.monitoring_utils`
3. For write operations, use `central_conn.command("POST"/"PUT"/"DELETE", path, ...)` directly
   (see how `pycentral/scopes/site.py` handles create/update/delete)
4. Use `generate_url(endpoint, "monitoring")` for URL construction
5. For `v1alpha2` endpoints, pass `version="v1alpha2"` to `execute_get` or `generate_url`
   (requires adding `"v1alpha2"` to `versions` list in `url_utils.py`)

### Adding a new service module

1. Create `pycentral/services/<name>.py`
2. Add `"services"` and/or `"notifications"` categories to `url_utils.CATEGORIES`
3. Use `generate_url(endpoint, "services")` for URL construction

### Adding a new config module

1. Create `pycentral/config/<name>.py`
2. Import and delegate to `Profiles` from `pycentral.profiles.profiles`
3. Document the profile-specific fields from the OpenAPI spec

### Docstring format

All methods must use reStructuredText docstrings. Include the API endpoint in the docstring:

```python
def get_switches(central_conn, filter_str=None, limit=100, next_page=1):
    """
    Retrieve a page of switches.

    This method makes an API call to the following endpoint - ``GET network-monitoring/v1/switches``

    :param central_conn: Central connection object.
    :type central_conn: NewCentralBase
    :param filter_str: Optional OData filter expression.
    :type filter_str: str, optional
    :param limit: Number of entries to return (max 100).
    :type limit: int, optional
    :param next_page: Pagination cursor (default 1).
    :type next_page: int, optional
    :return: API response dict with 'items', 'total', 'next'.
    :rtype: dict
    :raises ParameterError: If limit exceeds 100 or next_page < 1.
    """
```
