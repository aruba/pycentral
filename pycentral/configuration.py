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

import sys
from pycentral.url_utils import ConfigurationUrl, urlJoin
from pycentral.base_utils import console_logger

urls = ConfigurationUrl()
DEVICE_TYPES = ["IAP", "ArubaSwitch", "CX", "MobilityController"]
logger = console_logger("CONFIGURATION")

class Groups(object):
    """A python class consisting of functions to manage Aruba Central Groups via REST API
    """
    def get_groups(self, conn, offset=0, limit=20):
        """Get list of groups

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param offset: Pagination offset, defaults to 0
        :type offset: int, optional
        :param limit: Pagination limit with Max 20, defaults to 20
        :type limit: int, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.GROUPS["GET_ALL"]
        params = {
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_config_mode_groups(self, conn, groups):
        """For each group in the provided list, the configuration mode for Instant APs and Gateways is
        specified under the 'Wireless' field and for switches under the 'Wired' field. The configuration
        mode is specified as a boolean value indicating if the device type is managed using the template
        mode of configuration or not.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param groups: A list of group names with max of 20 groups.
        :type groups: list
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.GROUPS["GET_TEMPLATE_INFO"]
        params = {
                    "groups": ",".join(groups)
                 }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def create_group(self, conn, group_name, group_password, wired_template=False, wireless_template=False):
        """Create new group given a group name, group password and configuration mode(UI or
        template mode of configuration) to be set per device type.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of the group to be created.
        :type group_name: str
        :param group_password: Password for the group to be created
        :type group_password: str
        :param wired_template: Set to True to make the configuration mode for switches to template
            mode, defaults to False
        :type wired_template: bool, optional
        :param wireless_template: Set to True to make the configuration mode for IAPs and Gateways to template
            mode, defaults to False
        :type wireless_template: bool, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.GROUPS["CREATE"]
        data = self._build_group_payload(group_name, group_password, wired_template, wireless_template)
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def clone_create_group(self, conn, new_group_name, existing_group_name):
        """Clone and create new group from a given group with the given name. The configuration of the new
        group will be inherited from the given group.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param new_group_name: New group name to be created.
        :type new_group_name: str
        :param existing_group_name: Existing group name to be cloned.
        :type existing_group_name: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.GROUPS["CREATE_CLONE"]
        data = {
                    "group": new_group_name,
                    "clone_group": existing_group_name
                }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    # Not supported
    # def update_group(self):
    #     pass

    def delete_group(self, conn, group_name):
        """Delete an existin group

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of the group to be deleted.
        :type group_name: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.GROUPS["DELETE"], group_name)
        resp = conn.command(apiMethod="DELETE", apiPath=path)
        return resp

    def _build_group_payload(self, group_name, group_password, wired_template, wireless_template):
        """Build the HTTP payload for groups config

        :param group_name: Name of the group to be created.
        :type group_name: str
        :param group_password: Password for the group to be created
        :type group_password: str
        :param wired_template: Set to True to make the configuration mode for switches to template
            mode, defaults to False
        :type wired_template: bool
        :param wireless_template: Set to True to make the configuration mode for IAPs and Gateways to template
            mode, defaults to False
        :type wireless_template: bool
        :return: HTTP payload for groups config
        :rtype: dict
        """
        payload_json = {
            "group": group_name,
            "group_attributes": {
                "group_password": group_password,
                "template_info": {
                    "Wired": wired_template,
                    "Wireless": wireless_template
                }
            }
        }
        return payload_json

class Devices(object):
    """A python class consisting of functions to manage Aruba Central Devices via REST API
    """
    def get_devices_group(self, conn, device_serial):
        """Get group name for a device

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of Aruba device
        :type device_serial: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.DEVICES["GET"], device_serial, "group")
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def get_devices_configuration(self, conn, device_serial):
        """Get last known device configuration for a device.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of Aruba device.
        :type device_serial: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.DEVICES["GET"], device_serial, "configuration")
        headers = {
            "Accept": "multipart/form-data"
        }
        resp = conn.command(apiMethod="GET", apiPath=path, headers=headers)
        return resp

    def get_devices_config_details(self, conn, device_serial, details=True):
        """Get 1) central side configuration. 2) Device running configuration.
        3) Configuration error details. 4) Template error details and status of a device
        belonging to a template group.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of Aruba device.
        :type device_serial: str
        :param details: Usually pass false to get only the summary of a device's configuration status. Pass true only
            if detailed response of a device's configuration status is required. Passing true might result in slower API
            response and performance effect comparatively., defaults to True
        :type details: bool, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.DEVICES["GET"], device_serial, "config_details")
        params = {
            "details": details
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_devices_templates(self, conn, device_serials):
        """Get existing templates for list of devices

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serials: List of serial number of Aruba devices
        :type device_serials: list
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urls.DEVICES["GET_TEMPLATES"]
        params = {
            "device_serials": ",".join(device_serials)
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_devices_group_templates(self, conn, device_type="IAP", include_groups=[],
                                    exclude_groups=[], all_groups=False, offset=0, limit=20):
        """Get templates for devices in a group or multiple groups

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_type: Device type (i.e. IAP/ArubaSwitch/MobilityController/CX), defaults to "IAP"
        :type device_type: str, optional
        :param include_groups: Fetch devices templates in list of groups, defaults to []
        :type include_groups: list, optional
        :param exclude_groups: Fetch devices templates not in list of groups, defaults to []
        :type exclude_groups: list, optional
        :param all_groups: Set to True, to fetch devices templates details for all the groups
            (Only allowed for user having all_groups access or admin), defaults to False
        :type all_groups: bool, optional
        :param offset: Pagination offset, defaults to 0
        :type offset: int, optional
        :param limit: Pagination limit with Max 20, defaults to 20
        :type limit: int, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urls.DEVICES["GET_GRP_TEMPLATES"]
        params = {
            "limit": limit,
            "offset": offset,
            "device_type": device_type,
            "all_groups": all_groups
        }
        if include_groups:
            params["include_groups"] = ",".join(include_groups)
        if exclude_groups:
            params["exclude_groups"] = ",".join(exclude_groups)
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_device_templates_from_hash(self, conn, template_hash, offset=0, limit=20,
                                  exclude_hash=False, device_type="IAP"):
        """List of devices with its group name and template information is populated

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param template_hash: Template_hash of the template for which list of devices needs to be populated.
        :type template_hash: str
        :param offset: Pagination offset, defaults to 0
        :type offset: int, optional
        :param limit: Pagination limit with Max 20, defaults to 20
        :type limit: int, optional
        :param exclude_hash: Fetch devices template details not matching with provided hash, defaults to False
        :type exclude_hash: bool, optional
        :param device_type: Device type (i.e. IAP/ArubaSwitch/MobilityController/CX), defaults to "IAP"
        :type device_type: str, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.DEVICES["GET"], template_hash, "template")
        params = {
            "offset": offset,
            "limit": limit,
            "exclude_hash": exclude_hash,
            "device_type": device_type
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_switch_variablized_templates(self, conn, device_serial):
        """Get template and variabled for Aruba device (switch)

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of Aruba device.
        :type device_serial: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.DEVICES["GET"], device_serial, "variablised_template")
        headers = {
            "Accept": "multipart/form-data"
        }
        resp = conn.command(apiMethod="GET", apiPath=path, headers=headers)
        return resp

    def set_switch_ssh_credentials(self, conn, device_serial, username, password):
        """Set SSH connection information of Aruba Device (switch)

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of Aruba device.
        :type device_serial: str
        :param username: SSH username to set to the device
        :type username: str
        :param password: SSH password to set to the device
        :type password: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.DEVICES["SET_SWITCH_CRED"], device_serial, "ssh_connection")
        data = {
                    "username": username,
                    "password": password
                }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def move_devices(self, conn, group_name, device_serials):
        """Move list of devices to group and assign specified group in device management page

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of a group where devices will be moved
        :type group_name: str
        :param device_serials: A list of device serials to be moved to the mentioned group
        :type device_serials: list
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urls.DEVICES["MOVE_DEVICES"]
        data = {
            "group": group_name,
            "serials": device_serials
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

class Templates(object):
    """A python class consisting of functions to manage Aruba Central Templates via REST API
    """
    def get_template_text(self, conn, group_name, template_name):
        """Get CLI template in text format.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of an existing group
        :type group_name: str
        :param template_name: Name of an existing template within mentioned group
        :type template_name: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.TEMPLATES["GET"], group_name, "templates", template_name)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def get_template(self, conn, group_name, device_type="", template_name="", version="", model="", q="", offset=0, limit=20):
        """Get all templates in group. Query can be filtered by name, device_type, version, model or version number.
        Response is sorted by template name.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of the group for which the templates will be being queried.
        :type group_name: str
        :param device_type: Filter on device_type, defaults to ""
        :type device_type: str, optional
        :param template_name: Filter on template name, defaults to ""
        :type template_name: str, optional
        :param version: Filter on version property of template, defaults to ""
        :type version: str, optional
        :param model: Filter on model property of template. For 'ArubaSwitch' device_type, part number
            (J number) can be used., defaults to ""
        :type model: str, optional
        :param q: Search for template OR version OR model, q will be ignored if any of filter parameters are
            provided, defaults to ""
        :type q: str, optional
        :param offset: Pagination offset, defaults to 0
        :type offset: int, optional
        :param limit: Pagination limit with Max 20, defaults to 20
        :type limit: int, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.TEMPLATES["GET"], group_name, "templates")
        params = {
            "limit": limit,
            "offset": offset
        }
        if device_type:
            params["device_type"] = device_type
        if template_name:
            params["template"] = template_name
        if version:
            params["version"] = version
        if model:
            params["model"] = model
        if q:
            params["q"] = q
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def create_template(self, conn, group_name, template_name, template_filename, device_type="IAP", version="ALL", model="ALL"):
        """Upload a new template file

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of the group in which the template file will be created.
        :type group_name: str
        :param template_name: Name for the template to be created
        :type template_name: str
        :param template_filename: Name of the template file in local machine to be sent to central using API
        :type template_filename: str
        :param device_type: Type of the Aruba device, defaults to "IAP"
        :type device_type: str, optional
        :param version: Firmware version property of template., defaults to "ALL"
        :type version: str, optional
        :param model: Model property of template. For 'ArubaSwitch' device_type, part number (J number) can be
            used, defaults to "ALL"
        :type model: str, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        # Open template file in binary mode
        files = {}
        fp = None
        try:
            fp = open(template_filename, "rb")
            files = {
                        "template": fp
                    }
        except Exception as err:
            logger.error("Unable to open the template file! " + str(err))
            return None

        # Make the API request
        path = urlJoin(urls.TEMPLATES["CREATE"], group_name, "templates")
        params = {
                        "name": template_name,
                        "device_type": device_type,
                        "version": version,
                        "model": model
                    }
        resp = conn.command(apiMethod="POST", apiPath=path,
                            apiParams=params, files=files)

        # Close the file
        if fp:
            fp.close()

        return resp

    def update_template(self, conn, group_name, template_name, template_filename, device_type="", version="", model=""):
        """[summary]

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of the group in which the template file exists.
        :type group_name: str
        :param template_name: Name of the template to be modified
        :type template_name: str
        :param template_filename: Name of the template file in local machine to be sent to central using API
        :type template_filename: str
        :param device_type: Aruba device type of the template , defaults to ""
        :type device_type: str, optional
        :param version: Firmware version property of template., defaults to ""
        :type version: str, optional
        :param model: Device model property of template. For 'ArubaSwitch' device_type, part number (J number) can be
            used, defaults to ""
        :type model: str, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        # Open template file in binary mode
        files = {}
        fp = None
        try:
            fp = open(template_filename, "rb")
            files = {
                        "template": fp
                    }
        except Exception as err:
            logger.error("Unable to open the template file! " + str(err))
            return None

        path = urlJoin(urls.TEMPLATES["CREATE"], group_name, "templates")
        params = {
            "name": template_name
        }
        if device_type:
            params["device_type"] = device_type
        if version:
            params["version"] = version
        if model:
            params["model"] = model

        resp = conn.command(apiMethod="PATCH", apiPath=path,
                            apiParams=params, files=files)

        # Close the file
        if fp:
            fp.close()

        return resp

    def delete_template(self, conn, group_name, template_name):
        """Delete an existing template

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group_name: Name of the group in which the template file exists.
        :type group_name: str
        :param template_name: Name of the template to be deleted.
        :type template_name: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.TEMPLATES["GET"], group_name, "templates", template_name)
        resp = conn.command(apiMethod="DELETE", apiPath=path)
        return resp

class Variables(object):
    """A python class consisting of functions to manage Aruba Central Variables via REST API
    """
    def get_template_variables(self, conn, device_serial):
        """Get template variables for a device

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of the device.
        :type device_serial: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.VARIABLES["GET"], device_serial, "template_variables")
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def get_all_template_variables(self, conn, offset=0, limit=20, format="JSON"):
        """Get template variables for all devices

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param offset: Pagination offset. Number of items to be skipped before returning the data,
            useful for pagination, defaults to 0
        :type offset: int, optional
        :param limit: Pagination limit. Maximum number of records to be returned, defaults to 20
        :type limit: int, optional
        :param format: Format in which output is desired, defaults to "JSON"
        :type format: str, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urls.VARIABLES["GET_ALL"]
        params = {
            "format": format,
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def create_template_variables(self, conn, device_serial, variables):
        """Create template variable for a device

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial Number of a device for which the variables are to be created.
        :type device_serial: str
        :param variables: Variables defined in template file to be applied for a device
            Sample Variables {"_sys_serial": "AB0011111", "_sys_lan_mac": "11:12:AA:13:14:BB", "SSID_A": "Z-Employee"}
        :type variables: dict
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.VARIABLES["CREATE"], device_serial, "template_variables")
        data = {
                    "variables": variables
                }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def create_template_variables_file(self, conn, variables_filename, format="JSON"):
        """Create template variables for multiple devices defined in JSON format in a file

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param variables_filename: Name of the variable file to be sent to Central via API.
        :type variables_filename: str
        :param format: Format of data in the file to be uploaded, defaults to "JSON"
        :type format: str, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urls.VARIABLES["CREATE_ALL"]
        params = {
            "format": format
        }

        # Open variable file in binary mode
        files = {}
        fp = None
        try:
            fp = open(variables_filename, "rb")
            files = {
                        "variables": fp
                    }
        except Exception as err:
            logger.error("Unable to open the variable file! " + str(err))
            return None

        resp = conn.command(apiMethod="POST", apiPath=path,
                            apiParams=params, files=files)

        # Close the file
        if fp:
            fp.close()

        return resp

    def update_template_variables(self, conn, device_serial, variables):
        """Update values of existing template variables and add new variabels to the existing
        set of variables for a device.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of a device
        :type device_serial: str
        :param variables: Template variables to be updated for the mentioned device
        :type variables: dict
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.VARIABLES["UPDATE"], device_serial, "template_variables")
        data = {
            "variables": variables
        }
        resp = conn.command(apiMethod="PATCH", apiPath=path, apiData=data)
        return resp

    def update_template_variables_file(self, conn, variables_filename):
        """Update values of existing template variables and add new variabels to the existing
        set of variables for multiple devices defined in the specified file.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param variables_filename: Local filename of template variables to be uploaded to Central via API.
        :type variables_filename: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urls.VARIABLES["UPDATE_ALL"]

        # Open variable file in binary mode
        files = {}
        fp = None
        try:
            fp = open(variables_filename, "rb")
            files = {
                        "variables": fp
                    }
        except Exception as err:
            logger.error("Unable to open the variable file! " + str(err))
            return None

        resp = conn.command(apiMethod="PATCH", apiPath=path, files=files)

        # Close the file
        if fp:
            fp.close()

        return resp

    def replace_template_variables(self, conn, device_serial, variables):
        """Delete all existing template variables and create requested template variables for a device.
        This API can be used for deleting some variables out of all for a device.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of a device
        :type device_serial: str
        :param variables: Delete existing template variables for a device and replace with the new variables.
        :type variables: dict
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.VARIABLES["UPDATE"], device_serial, "template_variables")
        data = {
            "variables": variables
        }
        resp = conn.command(apiMethod="PUT", apiPath=path, apiData=data)
        return resp

    def replace_template_variables_file(self, conn, variables_filename, format="JSON"):
        """Delete all existing template variables and create requested template variables for all devices.
        This API can be used for deleting some variables out of all for all devices.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param variables_filename: filename of template variables to be uploaded to Central via API from local machine.
        :type variables_filename: str
        :param format: Data format of the specified file, defaults to "JSON"
        :type format: str, optional
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urls.VARIABLES["CREATE_ALL"]
        params = {
            "format": format
        }

        # Open variable file in binary mode
        files = {}
        fp = None
        try:
            fp = open(variables_filename, "rb")
            files = {
                        "variables": fp
                    }
        except Exception as err:
            logger.error("Unable to open the variable file! " + str(err))
            return None

        resp = conn.command(apiMethod="PUT", apiPath=path,
                            apiParams=params, files=files)

        # Close the file
        if fp:
            fp.close()

        return resp

    def delete_template_variables(self, conn, device_serial):
        """Delete all existing template variables for a device

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Serial number of a device
        :type device_serial: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.VARIABLES["DELETE"], device_serial, "template_variables")
        resp = conn.command(apiMethod="DELETE", apiPath=path)
        return resp

class ApSettings(object):
    """A Python class to manage AP settings such as AP name, zonename, etc.
    """
    def get_ap_settings(self, conn, serial_number: str):
        """Get existing AP settings

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param serial_number: Serial number of an AP. Example: CNBRHMV3HG
        :type serial_number: str
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.AP_SETTINGS["GET"], serial_number)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def update_ap_settings(self, conn, serial_number: str, ap_settings_data: dict):
        """Update Existing AP Settings

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param serial_number: Serial number of an AP. Example: CNBRHMV3HG
        :type serial_number: str
        :param ap_settings_data: Data to update ap settings. \n
            * keyword hostname: Name string to set to the AP \n
            * keyword ip_address: IP Address string to set to AP. Should be set to "0.0.0.0" if AP get IP from DHCP. \n
            * keyword zonename: Zonename string to set to AP \n
            * keyword achannel: achannel string to set to AP \n
            * keyword atxpower: atxpower string to set to AP \n
            * keyword gchannel: gchannel string to set to AP \n
            * keyword gtxpower: gtxpower string to set to AP \n
            * keyword dot11a_radio_disable: dot11a_radio_disable string to set to AP \n
            * keyword dot11g_radio_disable: dot11g_radio_disable string to set to AP \n
            * keyword usb_port_disable: usb_port_disable string to set to AP \n
        :type ap_settings_data: dict
        :return: Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`.
        :rtype: dict
        """
        path = urlJoin(urls.AP_SETTINGS["UPDATE"], serial_number)
        data = ap_settings_data
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp
