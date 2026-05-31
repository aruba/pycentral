# Monitoring

Monitoring modules available in the PyCentral SDK are separated by type APs, Clients, Devices, Gateways, Sites, and Switches.

---

## APs
::: pycentral.new_monitoring.aps

| Module name | API endpoint(s) | Description |
| --- | --- | --- |
| `get_all_aps` | `GET network-monitoring/v1/aps` | Retrieves all AP records by paging through the AP listing endpoint. |
| `get_aps` | `GET network-monitoring/v1/aps` | Retrieves a single page of AP records with optional filter and sort support. |
| `get_ap_details` | `GET network-monitoring/v1/aps/{serial_number}` | Retrieves details for a specific AP. |
| `get_ap_trends` | `GET network-monitoring/v1/aps/{serial_number}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/cpu-utilization-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/memory-utilization-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/power-consumption-trends` | Retrieves AP trend data for throughput, CPU, memory, or power consumption. |
| `get_all_radios` | `GET network-monitoring/v1/radios` | Retrieves all fleet radio records by handling pagination automatically. |
| `get_radios` | `GET network-monitoring/v1/radios` | Retrieves a single page of fleet radios. |
| `get_all_bssids` | `GET network-monitoring/v1/bssids` | Retrieves all fleet BSSID records by handling pagination automatically. |
| `get_bssids` | `GET network-monitoring/v1/bssids` | Retrieves a single page of fleet BSSIDs. |
| `get_all_swarms` | `GET network-monitoring/v1/swarms` | Retrieves all swarm records by handling pagination automatically. |
| `get_swarms` | `GET network-monitoring/v1/swarms` | Retrieves a single page of swarms. |
| `get_swarm_details` | `GET network-monitoring/v1/swarms/{cluster_id}` | Retrieves details for a specific swarm cluster. |
| `get_ap_radios` | `GET network-monitoring/v1/aps/{serial_number}/radios` | Retrieves radios associated with a specific AP. |
| `get_ap_radio_trends` | `GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/channel-utilization-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/channel-quality-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/noise-floor-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/frames-trends` | Retrieves trend data for a specific radio on an AP. |
| `get_ap_ports` | `GET network-monitoring/v1/aps/{serial_number}/ports` | Retrieves port information for a specific AP. |
| `get_ap_port_trends` | `GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/frames-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/crc-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/collisions-trends` | Retrieves trend data for a specific AP port. |
| `get_all_ap_tunnels` | `GET network-monitoring/v1/aps/{serial_number}/tunnels` | Retrieves all tunnel records for an AP by handling pagination automatically. |
| `get_ap_tunnels` | `GET network-monitoring/v1/aps/{serial_number}/tunnels` | Retrieves a single page of tunnel records for an AP. |
| `get_ap_tunnel_details` | `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}` | Retrieves details for a specific tunnel on an AP. |
| `get_ap_tunnel_trends` | `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/throughput-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/packet-loss-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/mos-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/jitter-trends`<br>`GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/latency-trends` | Retrieves trend data for a specific AP tunnel. |
| `get_ap_wlans` | `GET network-monitoring/v1/aps/{serial_number}/wlans` | Retrieves WLANs associated with a specific AP. |

---

## Clients
::: pycentral.new_monitoring.clients

---

## Devices
::: pycentral.new_monitoring.devices

---

## Gateways
::: pycentral.new_monitoring.gateways

| Module name | API endpoint(s) | Description |
| --- | --- | --- |
| `get_all_gateways` | `GET network-monitoring/v1/gateways` | Retrieves all gateways by paging through the gateway listing endpoint. |
| `get_gateways` | `GET network-monitoring/v1/gateways` | Retrieves a single page of gateway records with optional filter and sort support. |
| `get_gateway_details` | `GET network-monitoring/v1/gateways/{serial_number}` | Retrieves details for a specific gateway. |
| `get_all_gateway_ports` | `GET network-monitoring/v1/gateways/{serial_number}/ports` | Retrieves all gateway port records by handling pagination automatically. |
| `get_gateway_ports` | `GET network-monitoring/v1/gateways/{serial_number}/ports` | Retrieves a single page of gateway ports with optional filter and sort support. |
| `get_gateway_port_details` | `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}` | Retrieves details for a specific gateway port. |
| `get_all_gateway_vlans` | `GET network-monitoring/v1/gateways/{serial_number}/vlans` | Retrieves all gateway VLAN records by handling pagination automatically. |
| `get_gateway_vlans` | `GET network-monitoring/v1/gateways/{serial_number}/vlans` | Retrieves a single page of gateway VLANs with optional filter and sort support. |
| `get_gateway_vlan_details` | `GET network-monitoring/v1/gateways/{serial_number}/vlans/{vlan_id}` | Retrieves details for a specific gateway VLAN. |
| `get_all_gateway_tunnels` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels` | Retrieves all gateway tunnel records by handling pagination automatically. |
| `get_gateway_tunnels` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels` | Retrieves a single page of gateway tunnels with optional filter and sort support. |
| `get_gateway_tunnel_details` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}` | Retrieves details for a specific gateway tunnel. |
| `get_gateway_uplinks` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks` | Retrieves all uplinks for a gateway with optional sort support. |
| `get_gateway_uplink_details` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}` | Retrieves details for a specific gateway uplink. |
| `get_all_gateway_dhcp_pools` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-pools` | Retrieves all gateway DHCP pool records by handling pagination automatically. |
| `get_gateway_dhcp_pools` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-pools` | Retrieves a single page of gateway DHCP pools with optional sort support. |
| `get_all_gateway_dhcp_clients` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-clients` | Retrieves all gateway DHCP client records by handling pagination automatically. |
| `get_gateway_dhcp_clients` | `GET network-monitoring/v1/gateways/{serial_number}/dhcp-clients` | Retrieves a single page of gateway DHCP clients with optional filter and sort support. |
| `get_gateway_trends` | `GET network-monitoring/v1/gateways/{serial_number}/cpu-utilization-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/memory-utilization-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/wan-availability-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/vpn-availability-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/hardware-temperature-trends` | Retrieves gateway trend data for a specified metric (cpu-utilization, memory-utilization, wan-availability, vpn-availability, hardware-temperature). |
| `get_gateway_port_trends` | `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/throughput-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-errors-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-packets-trends` | Retrieves trend data for a gateway port metric (throughput, frames, frames-errors, frames-packets). |
| `get_gateway_tunnel_trends` | `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/throughput-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/status-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/dropped-packet-trends` | Retrieves trend data for a gateway tunnel metric (throughput, status, dropped-packets). |
| `get_gateway_uplink_trends` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/throughput-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-compression-trends`<br>`GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-availability-trends` | Retrieves trend data for a gateway uplink metric (throughput, wan-compression, wan-availability). |
| `get_gateway_uplink_vpn_availability_trends` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{vlan_id}/vpn-availability-trends` | Retrieves VPN availability trends for a gateway uplink using a VLAN identifier. |
| `get_gateway_uplink_probes` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/probes` | Retrieves probe definitions for a specific gateway uplink. |
| `get_gateway_uplink_probe_performance_trends` | `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/probes/{probe}/performance-trends` | Retrieves performance trends for a specific gateway uplink probe. |
| `get_gateway_tunnel_health_summary` | `GET network-monitoring/v1/gateways/{serial_number}/lan-tunnels-health-summary`<br>`GET network-monitoring/v1/gateways/{serial_number}/wan-tunnels-health-summary` | Retrieves LAN or WAN tunnel health summary for a gateway. |
| `get_all_cluster_members` | `GET network-monitoring/v1/clusters/{cluster_name}/members` | Retrieves all cluster member records by handling pagination automatically. |
| `get_cluster_members` | `GET network-monitoring/v1/clusters/{cluster_name}/members` | Retrieves a single page of cluster members with optional filter and sort support. |
| `get_all_cluster_tunnels` | `GET network-monitoring/v1/clusters/{cluster_name}/tunnels` | Retrieves all cluster tunnel records by handling pagination automatically. |
| `get_cluster_tunnels` | `GET network-monitoring/v1/clusters/{cluster_name}/tunnels` | Retrieves a single page of cluster tunnels with optional filter and sort support. |
| `get_cluster_vlan_mismatch` | `GET network-monitoring/v1/clusters/{cluster_name}/vlan-mismatch` | Retrieves VLAN mismatch details for a cluster. |
| `get_cluster_connectivity_graph` | `GET network-monitoring/v1/clusters/{cluster_name}/connectivity-graph` | Retrieves connectivity graph details for a cluster. |
| `get_cluster_tunnel_summary` | `GET network-monitoring/v1/clusters/{cluster_name}/tunnels-health-summary`<br>`GET network-monitoring/v1/clusters/{cluster_name}/tunnels-status-summary` | Retrieves cluster tunnel health or status summary. |
| `get_cluster_capacity_trends` | `GET network-monitoring/v1/clusters/{cluster_name}/capacity-trends`<br>`GET network-monitoring/v1/clusters/{cluster_name}/capacity-trends/{serial_number}` | Retrieves cluster capacity trends, optionally scoped to a specific cluster member by serial number. |

---

## Sites
::: pycentral.new_monitoring.sites

---

## Switches
::: pycentral.new_monitoring.switches


## WLANs
::: pycentral.new_monitoring.wlans

| Module name | API endpoint(s) | Description |
| --- | --- | --- |
| `get_all_wlans` | `GET network-monitoring/v1/wlans` | Retrieves all WLAN records by paging through the WLAN listing endpoint. |
| `get_wlans` | `GET network-monitoring/v1/wlans` | Retrieves a single page of WLAN records with optional site, AP serial, filter, and sort criteria. |
