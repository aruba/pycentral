# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def urlJoin(*args):
    trailing_slash = '/' if args[-1].endswith('/') else ''
    return "/" + "/".join(map(lambda x: str(x).strip('/'),
                          args)) + trailing_slash


class RefreshUrl(object):
    REFRESH_TOKEN = {
        "REFRESH": "/oauth2/token"
    }


class ConfigurationUrl():
    AP_SETTINGS = {
        "GET": "/configuration/v2/ap_settings",
        "UPDATE": "/configuration/v2/ap_settings"
    }

    AP_CONFIGURATION = {
        "GET": "/configuration/v1/ap_cli",
        "REPLACE": "/configuration/v1/ap_cli"
    }

    GROUPS = {
        "DELETE": "/configuration/v1/groups",
        "UPDATE": "/configuration/v1/groups",
        "GET_ALL": "/configuration/v2/groups",
        "GET_TEMPLATE_INFO": "/configuration/v2/groups/template_info",
        "CREATE": "/configuration/v2/groups",
        "CREATE_CLONE": "/configuration/v2/groups/clone"
    }

    TEMPLATES = {
        "GET": "/configuration/v1/groups",
        "CREATE": "/configuration/v1/groups",
        "UPDATE": "/configuration/v1/groups",
        "DELETE": "/configuration/v1/groups"
    }

    DEVICES = {
        "GET": "/configuration/v1/devices",
        "GET_TEMPLATES": "/configuration/v1/devices/template",
        "GET_GRP_TEMPLATES": "/configuration/v1/devices/groups/template",
        "SET_SWITCH_CRED": "/configuration/v1/devices",
        "MOVE_DEVICES": "/configuration/v1/devices/move"
    }

    VARIABLES = {
        "GET": "/configuration/v1/devices",
        "DELETE": "/configuration/v1/devices",
        "CREATE": "/configuration/v1/devices",
        "UPDATE": "/configuration/v1/devices",
        "REPLACE": "/configuration/v1/devices",
        "GET_ALL": "/configuration/v1/devices/template_variables",
        "CREATE_ALL": "/configuration/v1/devices/template_variables",
        "UPDATE_ALL": "/configuration/v1/devices/template_variables",
        "REPLACE_ALL": "/configuration/v1/devices/template_variables"
    }

    WLAN = {
        "GET": "/configuration/full_wlan",
        "GET_ALL": "/configuration/v1/wlan",
        "CREATE": "/configuration/v2/wlan",
        "CREATE_FULL": "/configuration/full_wlan",
        "DELETE": "/configuration/v1/wlan",
        "UPDATE": "/configuration/v2/wlan",
        "UPDATE_FULL": "/configuration/full_wlan"
    }


class LicensingUrl():
    SUBSCRIPTIONS = {
        "GET_KEYS": "/platform/licensing/v1/subscriptions",
        "GET_ENABLED_SVC": "/platform/licensing/v1/services/enabled",
        "ASSIGN": "/platform/licensing/v1/subscriptions/assign",
        "UNASSIGN": "/platform/licensing/v1/subscriptions/unassign",
        "GET_STATS": "/platform/licensing/v1/subscriptions/stats",
        "GET_LIC_SVC": "/platform/licensing/v1/services/config",
        "UNASSIGN_LIC": "/platform/licensing/v1/subscriptions/devices/all",
        "ASSIGN_LIC": "/platform/licensing/v1/subscriptions/devices/all",
        "UNASSIGN_LIC_MSP":
            "/platform/licensing/v1/msp/subscriptions/devices/all",
        "ASSIGN_LIC_MSP":
            "/platform/licensing/v1/msp/subscriptions/devices/all"}

    AUTO_LICENSE = {
        "GET_SVC": "/platform/licensing/v1/customer/settings/autolicense",
        "DISABLE_SVC": "/platform/licensing/v1/customer/settings/autolicense",
        "ASSIGN_LIC_SVC":
            "/platform/licensing/v1/customer/settings/autolicense",
        "DISABLE_LIC_SVC_MSP":
            "/platform/licensing/v1/msp/customer/settings/autolicense",
        "GET_LIC_SVC_MSP":
            "/platform/licensing/v1/msp/customer/settings/autolicense",
        "ASSIGN_LIC_SVC_MSP":
            "/platform/licensing/v1/msp/customer/settings/autolicense",
        "GET_SVC_LIC_TOK": "/platform/licensing/v1/autolicensing/services"}


class UserManagementUrl():
    USERS = {
        "LIST": "/accounts/v2/users",
        "GET_USERS": "/platform/rbac/v1/users",
        "GET": "/platform/rbac/v1/users",
        "CREATE": "/platform/rbac/v1/users",
        "UPDATE": "/platform/rbac/v1/users",
        "DELETE": "/platform/rbac/v1/users"
    }

    ROLES = {
        "GET_ROLES": "/platform/rbac/v1/roles",
        "GET": "/platform/rbac/v1/apps",
        "CREATE": "/platform/rbac/v1/apps",
        "UPDATE": "/platform/rbac/v1/apps",
        "DELETE": "/platform/rbac/v1/apps"
    }


class FirmwareManagementUrl():
    FIRMWARE = {
        "GET_ALL_SWARMS": "/firmware/v1/swarms",
        "GET_SWARM": "/firmware/v1/swarms",
        "GET_VERSIONS_IAP": "/firmware/v1/versions",
        "CHECK_VERSION_SUPPORT": "/firmware/v1/versions",
        "GET_STATUS": "/firmware/v1/status",
        "UPGRADE": "/firmware/v1/upgrade",
        "CANCEL": "/firmware/v1/upgrade/cancel"
    }


class TopoUrl():
    TOPOLOGY = {
        "GET_TOPO_SITE": "/topology_external_api",
        "GET_DEVICES": "/topology_external_api/devices",
        "GET_EDGES": "/topology_external_api/v2/edges",
        "GET_UPLINK": "/topology_external_api/uplinks",
        "GET_TUNNEL": "/topology_external_api/tunnels",
        "GET_AP_LLDP": "/topology_external_api/apNeighbors"
    }


class RapidsUrl():
    ROGUES = {
        "GET_ROGUE_AP": "/rapids/v1/rogue_aps",
        "GET_INTERFERING_AP": "/rapids/v1/interfering_aps",
        "GET_SUSPECT_AP": "/rapids/v1/suspect_aps",
        "GET_NEIGHBOR_AP": "/rapids/v1/neighbor_aps"
    }

    WIDS = {
        "GET_INFRA_ATTACKS": "/rapids/v1/wids/infrastructure_attacks",
        "GET_CLIENT_ATTACKS": "/rapids/v1/wids/client_attacks",
        "GET_WIDS_EVENTS": "/rapids/v1/wids/events"
    }


class AuditUrl():
    TRAIL_LOG = {
        "GET_ALL": "/platform/auditlogs/v1/logs",
        "GET": "/platform/auditlogs/v1/logs"
    }

    EVENT_LOG = {
        "GET_ALL": "/auditlogs/v1/events",
        "GET": "/auditlogs/v1/event_details"
    }


class VisualrfUrl():
    CLIENT_LOCATION = {
        "GET_CLIENT_LOC": "/visualrf_api/v1/client_location/",
        "GET_FLOOR_CLIENTS": "/visualrf_api/v1/floor"
    }

    ROGUE_LOCATION = {
        "GET_AP_LOC": "/visualrf_api/v1/rogue_location",
        "GET_FLOOR_APS": "/visualrf_api/v1/floor"
    }

    FLOOR_PLAN = {
        "GET_CAMPUS_LIST": "/visualrf_api/v1/campus",
        "GET_CAMPUS_INFO": "/visualrf_api/v1/campus",
        "GET_BUILDING_INFO": "/visualrf_api/v1/building",
        "GET_FLOOR_INFO": "/visualrf_api/v1/floor",
        "GET_FLOOR_IMG": "/visualrf_api/v1/floor",
        "GET_FLOOR_APS": "/visualrf_api/v1/floor",
        "GET_AP_LOC": "/visualrf_api/v1/access_point_location"
    }


class MonitoringUrl():
    SITES = {
        "GET_ALL": "/central/v2/sites",
        "CREATE": "/central/v2/sites",
        "DELETE": "/central/v2/sites",
        "UPDATE": "/central/v2/sites",
        "ADD_DEVICE": "/central/v2/sites/associate",
        "DELETE_DEVICE": "/central/v2/sites/associate",
        "ADD_DEVICES": "/central/v2/sites/associations",
        "DELETE_DEVICES": "/central/v2/sites/associations"
    }


class InventoryUrl():
    DEVICES = {
        "GET_DEVICES": "/platform/device_inventory/v1/devices",
        "ARCHIVE_DEVICES": "/platform/device_inventory/v1/devices/archive",
        "UNARCHIVE_DEVICES": "/platform/device_inventory/v1/devices/unarchive",
        "ADD_DEVICE": "/platform/device_inventory/v1/devices"
    }


class MspURL():
    MSP = {
        "V1_CUSTOMER": "/msp_api/v1/customers",
        "V2_CUSTOMER": "/msp_api/v2/customers",
        "COUNTRY_CODE": "/msp_api/v2/get_country_code",
        "USERS": "/msp_api/v1/customers/users",
        "RESOURCES": "/msp_api/v1/resource",
        "DEVICES": "/msp_api/v1/devices",
        "GROUPS": "/msp_api/v1/groups"
    }
