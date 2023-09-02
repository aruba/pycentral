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

from pycentral.url_utils import FirmwareManagementUrl, urlJoin
from pycentral.base_utils import console_logger

urls = FirmwareManagementUrl()


class Firmware():
    """A Python Class to manage Aruba Central Device Firmware via REST APIs.
    """

    def list_firmware_all_swarms(self, conn, group=None, limit=20, offset=0):
        """Get a list of swarms with their firmware details. You can \
            optionally specify a group, to filter devices under it

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: Name of the group, defaults to None
        :type group: str, optional
        :param limit: Pagination limit. Default is 20 and max is 1000,\
            defaults to 20
        :type limit: int, optional
        :param offset: Pagination offset, defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.FIRMWARE["GET_ALL_SWARMS"]
        params = {
            "offset": offset,
            "limit": limit
        }
        if group:
            params["group"] = group
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_firmware_swarm(self, conn, swarm_id):
        """Get firmware details for specific swarm.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param swarm_id: Swarm ID for which the firmware detail to be queried
        :type swarm_id: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.FIRMWARE["GET_SWARM"], swarm_id)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def list_supported_version(self, conn, device_type=None, swarm_id=None,
                               serial=None):
        """Get list of firmware versions for device. Specify device_type\
            "IAP"/"MAS"/"HP"/"CONTROLLER" to get firmware versions for swarms,\
            MAS switches, aruba switches and controllers respectively or you\
            can specify swarm_id to get list of supported version for specific\
            swarm or you can specify serial to get list of supported version\
            for specific device.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_type: Specify one of "IAP/MAS/HP/CONTROLLER", defaults\
            to None
        :type device_type: str, optional
        :param swarm_id: Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param serial: Serial of device, defaults to None
        :type serial: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.FIRMWARE["GET_VERSIONS_IAP"]
        params = {}
        if device_type:
            params["device_type"] = device_type
        elif swarm_id:
            params["swarm_id"] = swarm_id
        elif serial:
            params["serial"] = serial
        else:
            conn.logger.error(
                "Failed to check supported formware version! \
            Missing required parameter: device_type or swarm_id or serial!")
            return None
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def check_firmware_support(self, conn, firmware_version, device_type):
        """Check whether specific firmware version is available or not.\
            Specify device_type "IAP"/"MAS"/"HP"/"CONTROLLER" to get firmware\
            versions for swarms/MAS switches/aruba switches/controllers\
            respectively.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param firmware_version: Firmware Version
        :type firmware_version: str
        :param device_type: Specify one of "IAP/MAS/HP/CONTROLLER"
        :type device_type: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(
            urls.FIRMWARE["CHECK_VERSION_SUPPORT"],
            firmware_version)
        print("DEbug!! ", path)
        params = {
            "device_type": device_type
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def check_firmware_status(self, conn, serial=None, swarm_id=None):
        """Get firmware upgrade status of device. You can either specify\
            swarm_id if device_type is
        "IAP" or serial for rest of device_type, but not both.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param serial: Serial of device, defaults to None
        :type serial: str, optional
        :param swarm_id: Swarm ID, defaults to None
        :type swarm_id: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.FIRMWARE["GET_STATUS"]
        params = {}
        if swarm_id:
            params["swarm_id"] = swarm_id
        elif serial:
            params["serial"] = serial
        else:
            conn.logger.error("Failed to Check Firmware Status! \
                Missing parameters serial or swarm_id!")
            return None
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def upgrade_firmware(self, conn, firmware_version, reboot=True,
                         device_type=None, model=None, group=None, serial=None,
                         swarm_id=None, schedule_at=None):
        """Upgrade firmware version for a device or for a whole group of\
            devices under a device type, with additional filter of model. To\
            initiate upgrade for certain type of devices of specific group,\
            specify device_type as one of "IAP" for swarm, "MAS" for MAS\
            switches, "HP" for aruba switches, "CONTROLLER" for controllers\
            respectively, and group name. To upgrade a device, you can specify\
            swarm_id to upgrade a specific swarm or serial to upgrade a\
            specific device. To upgrade a specific model of Aruba switches at\
            group level, please use model in request body.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param firmware_version: Specify firmware version to which you want\
            device to upgrade. If you do not specify this field then firmware\
            upgrade initiated with recommended firmware version
        :type firmware_version: str
        :param reboot: Use True for auto reboot after successful firmware\
            download. Default value is False. Applicable only on MAS, Aruba\
            switches and controller since IAP reboots automatically after \
            firmware download., defaults to True
        :type reboot: bool, optional
        :param device_type: Specify one of "IAP/MAS/HP/CONTROLLER", defaults\
            to None
        :type device_type: str, optional
        :param model: To initiate upgrade at group level for specific model\
            family. Applicable only for Aruba switches, defaults to None
        :type model: str, optional
        :param group: Specify Group Name to initiate upgrade for whole group.,\
            defaults to None
        :type group: str, optional
        :param serial: Serial of device, defaults to None
        :type serial: str, optional
        :param swarm_id: Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param schedule_at: Firmware upgrade will be scheduled at, \
            `firmware_scheduled_at` - current time. firmware_scheduled_at is\
            epoch in seconds and default value is current time, defaults to\
            None
        :type schedule_at: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.FIRMWARE["UPGRADE"]
        data = {
            "firmware_version": firmware_version,
            "reboot": reboot
        }
        if model:
            data["model"] = model
        if group:
            data["group"] = group
        if serial:
            data["serial"] = serial
        if device_type:
            data["device_type"] = device_type
        if swarm_id:
            data["swarm_id"] = swarm_id
        if schedule_at:
            data["firmware_scheduled_at"] = schedule_at
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def cancel_scheduled_upgrade(self, conn, serial=None, swarm_id=None,
                                 device_type=None, group=None):
        """Cancel scheduled firmware upgrade for a device or for a whole group\
            of devices. To cancel scheduled upgrade for certain type of\
            devices of specific group, specify device_type as one of "IAP" for\
            swarm, "MAS" for MAS switches, "HP" for aruba switches,\
            "CONTROLLER" for controllers respectively, and the group as the\
            group name. To cancel scheduled upgrade a device, you can specify\
            swarm_id of the specific swarm or serial of the specific device.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param serial: Serial of device, defaults to None
        :type serial: str, optional
        :param swarm_id: Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param device_type: Specify one of "IAP/MAS/HP/CONTROLLER", defaults\
            to None
        :type device_type: str, optional
        :param group: Specify Group Name to initiate upgrade for whole group,\
            defaults to None
        :type group: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.FIRMWARE["CANCEL"]
        data = {}
        if serial:
            data["serial"] = serial
        if swarm_id:
            data["swarm_id"] = swarm_id
        if device_type:
            data["device_type"] = device_type
        if group:
            data["group"] = group
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp
