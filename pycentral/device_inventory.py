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

from pycentral.url_utils import InventoryUrl
from pycentral.base_utils import console_logger

logger = console_logger("DEVICE INVENTORY")
urls = InventoryUrl()

MAX_DEVICES = 100


class Inventory(object):
    """
    A python class consisting of functions to manage Aruba Central inventory
    from the new device inventory category via REST API.
    """

    def get_inventory(self, conn, sku_type="all", limit=0, offset=0):
        """Get device details from inventory.

        :param conn: Instance of class:`pycentral.ArubaCentralBase`.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param sku_type: target device sku type to pull from inventory.
            Acceptable arguments: all, iap, switch, controller, gateway,
            vgw, cap, boc, all_ap, all_controller, others.
        :type sku_type: str
        :param limit: Pagination limit. Defaults to 0, which is intrepreted as
            get all. Maximum limit per request is 50.
        :type limit: int, optional
        :param offset: Pagination offset, defaults to 0.
        :type offset: int, optional

        :return: HTTP Response as provided by 'command' function in
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """

        path = urls.DEVICES["GET_DEVICES"]

        # Check limit for default.
        if limit != 0:
            params = {
                "limit": limit,
                "offset": offset,
                "sku_type": sku_type
            }
        else:
            # No limit param to allow get all devices.
            params = {
                "offset": offset,
                "sku_type": sku_type
            }

        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def archive_devices(self, conn, device_serials=[]):
        """Archive a list of devices using serial numbers

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serials: List of serial number of Aruba devices that\
            should be archived
        :type device_serials: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.DEVICES["ARCHIVE_DEVICES"]
        if isinstance(device_serials, str):
            device_serials = [device_serials]
        if (len(device_serials)) > MAX_DEVICES:
            logger.error(
                'Unable to archive more than {MAX_DEVICES} devices per API \
                call. Please archive {MAX_DEVICES} or less devices at a time.')
            return
        if len(device_serials) == 0:
            logger.error(
                "Unable to archive devices since no device serial numbers were\
                provided. Please provide atleast one device's details in the\
                device_serials function argument.")
            return

        apiData = {
            "serials": device_serials
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=apiData)
        # Devices in the succeeded_devices list
        successful_devices = [device["serial_number"]
                              for device in resp['msg']['succeeded_devices']]
        # Devices in the failed_devices list
        failed_devices = [device["serial_number"]
                          for device in resp['msg']['failed_devices']]
        if (resp["code"] == 200 and len(failed_devices) == 0):
            logger.info(
                f'Successfully archived devices with SN - \
                    {", ".join(str(device) for device in successful_devices)}')
        elif (resp["code"] == 200 and len(failed_devices) > 0):
            logger.error(
                f'Failed to archive devices with SN - \
                    {", ".join(str(device) for device in failed_devices)}')
            if (len(successful_devices) > 0):
                logger.info(
                    f'Successfully unarchived devices with SN - \
                    {", ".join(str(device) for device in successful_devices)}')
        else:
            logger.error(
                f'Error in API Response. Response Code - {resp["code"]}')
        return resp

    def unarchive_devices(self, conn, device_serials=[]):
        """Unarchive a list of devices using serial numbers

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serials: List of serial number of Aruba devices that\
            should be unarchived
        :type device_serials: list
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.DEVICES["UNARCHIVE_DEVICES"]
        if isinstance(device_serials, str):
            device_serials = [device_serials]

        if (len(device_serials)) > MAX_DEVICES:
            logger.error(
                'Unable to unarchive more than {MAX_DEVICES} devices per API\
                call. Please unarchive {MAX_DEVICES} or less devices at a\
                time.')
            return
        if len(device_serials) == 0:
            logger.error("Unable to unarchive devices since no device serial \
                         numbers were provided. Please provide atleast one \
                         device's details in the device_serials function \
                         argument.")
            return

        apiData = {
            "serials": device_serials
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=apiData)
        # Devices in the succeeded_devices list
        successful_devices = [device["serial_number"]
                              for device in resp['msg']['succeeded_devices']]
        # Devices in the failed_devices list
        failed_devices = [device["serial_number"]
                          for device in resp['msg']['failed_devices']]
        if (resp["code"] == 200 and len(failed_devices) == 0):
            logger.info(
                f'Successfully unarchived devices with SN - \
                {", ".join(str(device) for device in successful_devices)}')
        elif (resp["code"] == 200 and len(failed_devices) > 0):
            logger.error(
                f'Failed to unarchive devices with SN - \
                    {", ".join(str(device) for device in failed_devices)}')
            if (len(successful_devices) > 0):
                logger.info(
                    f'Successfully unarchived devices with SN - \
                    {", ".join(str(device) for device in successful_devices)}')
        else:
            logger.error(
                f'Error in API Response. Response Code - {resp["code"]}')
        return resp

    def add_devices(self, conn, device_details):
        """Add device(s) using Mac & Serial Numbers

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_details: List of dictionaries with Aruba devices that\
            should be added to the Aruba Central account. Each item in the\
            dictionary should have the following keys - `mac` & `serial`. For\
            Central On-Premises account, an additional key is required in the\
            dictionary - `partNumber`
        :type device_details: list
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if (len(device_details)) > MAX_DEVICES:
            logger.error(
                'Unable to add more than {MAX_DEVICES} devices per API call.\
                Please add {MAX_DEVICES} or less devices at a time.')
            return
        if len(device_details) == 0:
            logger.error(
                "No device details were provided. Please provide atleast one\
                device's details in the device_details function argument.")
            return

        path = urls.DEVICES["ADD_DEVICE"]
        apiData = device_details
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=apiData)
        extra_resp = None
        if 'extra' in resp['msg']:
            extra_resp = resp['msg']['extra']
        if (resp["code"] == 200):
            avail_devices = extra_resp['message']["available_device"]
            device_serials = [device["serial_number"] for device in avail_devices]
            logger.info(
                f'Successfully added devices(with SN - \
                {", ".join(str(device) for device in device_serials)}) \
                to Greenlake Device Inventory.')
        elif (resp["code"] == 400 and extra_resp is not None):
            if (extra_resp['error_code'] == 'ATHENA_ERROR_NO_DEVICE' and
                    len(error_devices) > 0):
                # Devices that were in the available_list
                successful_devices = extra_resp['message']["available_device"]
                # Devices that were either on the blocked_list or invalid_list
                error_devices = extra_resp['message']['blocked_device'] + \
                    extra_resp['message']['invalid_device']
                logger.error(
                    'Some or all of the devices were not added to the device\
                    inventory.')
                for device in error_devices:
                    logger.error(
                        f'Unable to add device({device["serial"]}). Reason for\
                            error - {device["ccs_message"]}')
                for device in successful_devices:
                    logger.info(
                        f'Able to add device({device["serial"]}). Reason for\
                            error - {device["ccs_message"]}')
        else:
            logger.error(
                f'Error in API Response. Response Code - {resp["code"]}, Error\
                    Message - {resp["msg"]["detail"]}')
        return resp
