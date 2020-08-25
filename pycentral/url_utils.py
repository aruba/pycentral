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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class UrlObj(object):

    def urlJoin(self, *args):
        trailing_slash = '/' if args[-1].endswith('/') else ''
        return "/".join(map(lambda x: str(x).strip('/'), args)) + trailing_slash

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

    REFRESH_TOKEN = {
        "REFRESH": "/oauth2/token"
    }

    SUBSCRIPTIONS = {
        "GET_KEYS": "/platform/licensing/v1/subscriptions",
        "GET_ENABLED_SVC": "/platform/licensing/v1/services/enabled",
        "ASSIGN": "/platform/licensing/v1/subscriptions/assign",
        "UNASSIGN": "/platform/licensing/v1/subscriptions/unassign",
        "GET_STATS": "/platform/licensing/v1/subscriptions/stats",
        "GET_LIC_SVC": "/platform/licensing/v1/services/config",
        "UNASSIGN_LIC": "/platform/licensing/v1/subscriptions/devices/all",
        "ASSIGN_LIC": "/platform/licensing/v1/subscriptions/devices/all",
        "UNASSIGN_LIC_MSP": "/platform/licensing/v1/msp/subscriptions/devices/all",
        "ASSIGN_LIC_MSP": "/platform/licensing/v1/msp/subscriptions/devices/all"
    }

    AUTO_LICENSE = {
        "GET_SVC": "/platform/licensing/v1/customer/settings/autolicense",
        "DISABLE_SVC": "/platform/licensing/v1/customer/settings/autolicense",
        "ASSIGN_LIC_SVC": "/platform/licensing/v1/customer/settings/autolicense",
        "DISABLE_LIC_SVC_MSP": "/platform/licensing/v1/msp/customer/settings/autolicense",
        "GET_LIC_SVC_MSP": "/platform/licensing/v1/msp/customer/settings/autolicense",
        "ASSIGN_LIC_SVC_MSP": "/platform/licensing/v1/msp/customer/settings/autolicense",
        "GET_SVC_LIC_TOK": "/platform/licensing/v1/autolicensing/services"
    }

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

    AP_SETTINGS = {
        "GET": "/configuration/v2/ap_settings",
        "UPDATE": "/configuration/v2/ap_settings"
    }