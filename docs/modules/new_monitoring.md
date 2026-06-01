# Monitoring

The `new_monitoring` module provides wrappers around the Central network monitoring REST API. Modules are organized by resource type: APs, Clients, Devices, Gateways, Sites, Switches, and WLANs.

---

## APs

### Access Points

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_aps` | `GET network-monitoring/v1/aps` | Retrieves all AP records by paging through the AP listing endpoint. |
| `get_aps` | `GET network-monitoring/v1/aps` | Retrieves a single page of AP records with optional filter and sort support. |
| `get_ap_details` | `GET network-monitoring/v1/aps/{serial_number}` | Retrieves details for a specific AP. |
| `get_ap_trends` | `GET network-monitoring/v1/aps/{serial_number}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/cpu-utilization-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/memory-utilization-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/power-consumption-trends` | Retrieves AP trend data for throughput, CPU, memory, or power consumption. |
| `get_ap_wlans` | `GET network-monitoring/v1/aps/{serial_number}/wlans` | Retrieves WLANs associated with a specific AP. |
| `get_ap_ports` | `GET network-monitoring/v1/aps/{serial_number}/ports` | Retrieves port information for a specific AP. |
| `get_ap_port_trends` | `GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/frames-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/crc-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/collisions-trends` | Retrieves trend data for a specific AP port. |

### Radios

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_radios` | `GET network-monitoring/v1/radios` | Retrieves all fleet radio records by handling pagination automatically. |
| `get_radios` | `GET network-monitoring/v1/radios` | Retrieves a single page of fleet radios. |
| `get_ap_radios` | `GET network-monitoring/v1/aps/{serial_number}/radios` | Retrieves radios associated with a specific AP. |
| `get_ap_radio_trends` | `GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/channel-utilization-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/channel-quality-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/noise-floor-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/frames-trends` | Retrieves trend data for a specific radio on an AP. |

### BSSIDs

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_bssids` | `GET network-monitoring/v1/bssids` | Retrieves all fleet BSSID records by handling pagination automatically. |
| `get_bssids` | `GET network-monitoring/v1/bssids` | Retrieves a single page of fleet BSSIDs. |

### Swarms

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_swarms` | `GET network-monitoring/v1/swarms` | Retrieves all swarm records by handling pagination automatically. |
| `get_swarms` | `GET network-monitoring/v1/swarms` | Retrieves a single page of swarms. |
| `get_swarm_details` | `GET network-monitoring/v1/swarms/{cluster_id}` | Retrieves details for a specific swarm cluster. |

### AP Tunnels

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_ap_tunnels` | `GET network-monitoring/v1/aps/{serial_number}/tunnels` | Retrieves all tunnel records for an AP by handling pagination automatically. |
| `get_ap_tunnels` | `GET network-monitoring/v1/aps/{serial_number}/tunnels` | Retrieves a single page of tunnel records for an AP. |
| `get_ap_tunnel_details` | `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}` | Retrieves details for a specific tunnel on an AP. |
| `get_ap_tunnel_trends` | `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/packet-loss-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/mos-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/jitter-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/latency-trends` | Retrieves trend data for a specific AP tunnel. |

### Module Reference

::: pycentral.new_monitoring.aps

---

## Clients

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_clients` | `GET network-monitoring/v1/clients` | Retrieves all clients by handling pagination automatically. |
| `get_clients` | `GET network-monitoring/v1/clients` | Retrieves a single page of clients with optional filter and sort support. |
| `get_wireless_clients` | `GET network-monitoring/v1/clients` | Retrieves all wireless clients, optionally scoped to a site or device. |
| `get_wired_clients` | `GET network-monitoring/v1/clients` | Retrieves all wired clients, optionally scoped to a site or device. |
| `get_connected_clients` | `GET network-monitoring/v1/clients` | Retrieves all connected clients, optionally scoped to a site or device. |
| `get_failed_clients` | `GET network-monitoring/v1/clients` | Retrieves all failed clients, optionally scoped to a site or device. |
| `get_clients_associated_device` | `GET network-monitoring/v1/clients` | Retrieves all clients associated with a specific device. |
| `get_client_details` | `GET network-monitoring/v1/clients/{client_mac}` | Retrieves details for a specific client by MAC address. |
| `get_client_trends` | `GET network-monitoring/v1/clients-trend` | Retrieves client trend data, optionally scoped to a site or device. |
| `get_top_n_clients` | `GET network-monitoring/v1/clients-topn-usage` | Retrieves the top-N clients by usage, optionally scoped to a site or device. |

### Module Reference

::: pycentral.new_monitoring.clients

---

## Devices

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_devices` | `GET network-monitoring/v1/devices` | Retrieves all onboarded and monitored devices by handling pagination automatically. |
| `get_devices` | `GET network-monitoring/v1/devices` | Retrieves a single page of onboarded devices with optional filter and sort support. |
| `get_all_device_inventory` | `GET network-monitoring/v1/device-inventory` | Retrieves all devices from the account inventory (including un-onboarded devices) by handling pagination automatically. |
| `get_device_inventory` | `GET network-monitoring/v1/device-inventory` | Retrieves a single page of device inventory records. |
| `delete_device` | `DELETE network-monitoring/v1/devices/{serial_number}` | Deletes a device from Central monitoring (device must be OFFLINE). |

### Module Reference

::: pycentral.new_monitoring.devices

---

## Gateways

### Gateways

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_gateways` | `GET network-monitoring/v1/gateways` | Retrieves all gateways by paging through the gateway listing endpoint. |
| `get_gateways` | `GET network-monitoring/v1/gateways` | Retrieves a single page of gateway records with optional filter and sort support. |
| `get_gateway_details` | `GET network-monitoring/v1/gateways/{serial_number}` | Retrieves details for a specific gateway. |
| `get_gateway_trends` | `GET network-monitoring/v1/gateways/{serial_number}/cpu-utilization-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/memory-utilization-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/wan-availability-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/vpn-availability-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/hardware-temperature-trends` | Retrieves gateway trend data for a specified metric (cpu-utilization, memory-utilization, wan-availability, vpn-availability, hardware-temperature). |

### Ports

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_gateway_ports` | `GET network-monitoring/v1/gateways/{serial_number}/ports` | Retrieves all gateway port records by handling pagination automatically. |
| `get_gateway_ports` | `GET network-monitoring/v1/gateways/{serial_number}/ports` | Retrieves a single page of gateway ports with optional filter and sort support. |
| `get_gateway_port_details` | `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}` | Retrieves details for a specific gateway port. |
| `get_gateway_port_trends` | `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/throughput-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-errors-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-packets-trends` | Retrieves trend data for a gateway port metric (throughput, frames, frames-errors, frames-packets). |

### VLANs

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_gateway_vlans` | `GET network-monitoring/v1/gateways/{serial_number}/vlans` | Retrieves all gateway VLAN records by handling pagination automatically. |
| `get_gateway_vlans` | `GET network-monitoring/v1/gateways/{serial_number}/vlans` | Retrieves a single page of gateway VLANs with optional filter and sort support. |
| `get_gateway_vlan_details` | `GET network-monitoring/v1/gateways/{serial_number}/vlans/{vlan_id}` | Retrieves details for a specific gateway VLAN. |

### Tunnels

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_gateway_tunnels` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels` | Retrieves all gateway tunnel records by handling pagination automatically. |
| `get_gateway_tunnels` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels` | Retrieves a single page of gateway tunnels with optional filter and sort support. |
| `get_gateway_tunnel_details` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}` | Retrieves details for a specific gateway tunnel. |
| `get_gateway_tunnel_trends` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/throughput-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/status-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/dropped-packet-trends` | Retrieves trend data for a gateway tunnel metric (throughput, status, dropped-packets). |
| `get_gateway_tunnel_health_summary` | `GET network-monitoring/v1/gateways/{serial_number}/lan-tunnels-health-summary`<br>`GET network-monitoring/v1/gateways/{serial_number}/wan-tunnels-health-summary` | Retrieves LAN or WAN tunnel health summary for a gateway. |

### Uplinks

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_gateway_uplinks` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks` | Retrieves all uplinks for a gateway with optional sort support. |
| `get_gateway_uplink_details` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}` | Retrieves details for a specific gateway uplink. |
| `get_gateway_uplink_trends` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/throughput-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-compression-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-availability-trends` | Retrieves trend data for a gateway uplink metric (throughput, wan-compression, wan-availability). |
| `get_gateway_uplink_vpn_availability_trends` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{vlan_id}/vpn-availability-trends` | Retrieves VPN availability trends for a gateway uplink using a VLAN identifier. |
| `get_gateway_uplink_probes` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/probes` | Retrieves probe definitions for a specific gateway uplink. |
| `get_gateway_uplink_probe_performance_trends` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/probes/{probe}/performance-trends` | Retrieves performance trends for a specific gateway uplink probe. |

### DHCP

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_gateway_dhcp_pools` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-pools` | Retrieves all gateway DHCP pool records by handling pagination automatically. |
| `get_gateway_dhcp_pools` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-pools` | Retrieves a single page of gateway DHCP pools with optional sort support. |
| `get_all_gateway_dhcp_clients` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-clients` | Retrieves all gateway DHCP client records by handling pagination automatically. |
| `get_gateway_dhcp_clients` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-clients` | Retrieves a single page of gateway DHCP clients with optional filter and sort support. |

### Clusters

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_cluster_members` | `GET network-monitoring/v1/clusters/{cluster_name}/members` | Retrieves all cluster member records by handling pagination automatically. |
| `get_cluster_members` | `GET network-monitoring/v1/clusters/{cluster_name}/members` | Retrieves a single page of cluster members with optional filter and sort support. |
| `get_all_cluster_tunnels` | `GET network-monitoring/v1/clusters/{cluster_name}/tunnels` | Retrieves all cluster tunnel records by handling pagination automatically. |
| `get_cluster_tunnels` | `GET network-monitoring/v1/clusters/{cluster_name}/tunnels` | Retrieves a single page of cluster tunnels with optional filter and sort support. |
| `get_cluster_vlan_mismatch` | `GET network-monitoring/v1/clusters/{cluster_name}/vlan-mismatch` | Retrieves VLAN mismatch details for a cluster. |
| `get_cluster_connectivity_graph` | `GET network-monitoring/v1/clusters/{cluster_name}/connectivity-graph` | Retrieves connectivity graph details for a cluster. |
| `get_cluster_tunnel_summary` | `GET network-monitoring/v1/clusters/{cluster_name}/tunnels-health-summary`<br>`GET network-monitoring/v1/clusters/{cluster_name}/tunnels-status-summary` | Retrieves cluster tunnel health or status summary. |
| `get_cluster_capacity_trends` | `GET network-monitoring/v1/clusters/{cluster_name}/capacity-trends`<br>`GET network-monitoring/v1/clusters/{cluster_name}/capacity-trends/{serial_number}` | Retrieves cluster capacity trends, optionally scoped to a specific cluster member by serial number. |

### Module Reference

::: pycentral.new_monitoring.gateways

---

## Sites

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_sites` | `GET network-monitoring/v1/sites-health` | Retrieves all sites, including health details, by handling pagination automatically. |
| `get_sites` | `GET network-monitoring/v1/sites-health` | Retrieves a single page of site health information. |
| `list_sites_device_health` | `GET network-monitoring/v1/sites-device-health` | Retrieves per-site device health statistics (count of poor, fair, and good devices). |
| `list_site_information` | `GET network-monitoring/v1/site-health/{site_id}` | Retrieves detailed health information for a specific site. |

### Module Reference

::: pycentral.new_monitoring.sites

---

## Switches

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_switches` | `GET network-monitoring/v1/switches` | Retrieves all switches by paging through the switch listing endpoint. |
| `get_switches` | `GET network-monitoring/v1/switches` | Retrieves a single page of switch records with optional filter and sort support. |
| `get_switch_details` | `GET network-monitoring/v1/switches/{serial_number}` | Retrieves details for a specific switch by serial number, stack ID, or conductor serial. |
| `get_stack_members` | `GET network-monitoring/v1/stack/{serial_number}/members` | Retrieves stack member details for a given stack ID or conductor serial. |
| `get_switch_hardware_categories` | `GET network-monitoring/v1/switches/{serial_number}/hardware-categories` | Retrieves hardware details for a specific switch. |
| `get_switch_lag` | `GET network-monitoring/v1/switches/{serial_number}/lag` | Retrieves link aggregation group (LAG) summary details for a specific switch. |
| `get_switch_interfaces` | `GET network-monitoring/v1/switches/{serial_number}/interfaces` | Retrieves interface details for a specific switch with optional filter, search, and sort support. |
| `get_switch_vlans` | `GET network-monitoring/v1/switches/{serial_number}/vlans` | Retrieves VLAN details for a specific switch with optional filter, search, and sort support. |
| `get_switch_interface_poe` | `GET network-monitoring/v1/switches/{serial_number}/interface-poe` | Retrieves interface PoE details for a specific switch. |
| `get_switch_vsx` | `GET network-monitoring/v1/switches/{serial_number}/vsx` | Retrieves Virtual Switching Extension (VSX) configuration and operational details for a specific switch. |
| `get_topn_interface_trends` | `GET network-monitoring/v1/switches/topn-interface-trends` | Retrieves top-N switch interface trends (rx bytes, tx bytes) for a site over a given time period. |
| `get_switch_interface_trends` | `GET network-monitoring/v1/switches/{serial_number}/interface-trends` | Retrieves interface trend data (RX/TX bytes, discards, errors, etc.) for a specific switch. |
| `get_switch_hardware_trends` | `GET network-monitoring/v1/switches/{serial_number}/hardware-trends` | Retrieves hardware trend data (CPU, memory, PoE) for a specific switch. |

### Module Reference

::: pycentral.new_monitoring.switches

---

## WLANs

| Method | API Endpoint(s) | Description |
| --- | --- | --- |
| `get_all_wlans` | `GET network-monitoring/v1/wlans` | Retrieves all WLAN records by paging through the WLAN listing endpoint. |
| `get_wlans` | `GET network-monitoring/v1/wlans` | Retrieves a single page of WLAN records with optional site, AP serial, filter, and sort criteria. |

### Module Reference

::: pycentral.new_monitoring.wlans
