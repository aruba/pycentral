# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

"""Constants for the new_monitoring module.

Defines API pagination limits used across monitoring classes.
"""

AP_LIMIT = 1000
RADIO_LIMIT = 1000
BSSID_LIMIT = 1000
SWARM_LIMIT = 1000
TUNNEL_LIMIT = 1000
GATEWAY_LIMIT = 100
GATEWAY_VLAN_LIMIT = 100
GATEWAY_DHCP_LIMIT = 100
CLUSTER_LIMIT = 100
SWITCH_LIMIT = 1000
DEVICE_LIMIT = 1000
SITE_LIMIT = 100
CLIENT_LIMIT = 1000
WLAN_LIMIT = 1000

__all__ = [
    "AP_LIMIT",
    "RADIO_LIMIT",
    "BSSID_LIMIT",
    "SWARM_LIMIT",
    "TUNNEL_LIMIT",
    "GATEWAY_LIMIT",
    "GATEWAY_VLAN_LIMIT",
    "GATEWAY_DHCP_LIMIT",
    "CLUSTER_LIMIT",
    "SWITCH_LIMIT",
    "DEVICE_LIMIT",
    "SITE_LIMIT",
    "CLIENT_LIMIT",
    "WLAN_LIMIT",
]
