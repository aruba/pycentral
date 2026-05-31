from ..utils.monitoring_utils import execute_get
from ..exceptions import ParameterError
from .constants import DEVICE_LIMIT

MONITOR_TYPE = "devices"


class MonitoringDevices:
    @staticmethod
    def get_all_devices(central_conn, filter_str=None, sort=None):
        """
        Retrieve all devices that are onboarded and currently being monitored in new Central.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): Processed list of all devices.
        """
        devices = []
        total_devices = None
        limit = DEVICE_LIMIT
        next = 1
        while True:
            response = MonitoringDevices.get_devices(
                central_conn, filter_str=filter_str, limit=limit, next=next
            )
            if total_devices is None:
                total_devices = response.get("total", 0)
            devices.extend(response.get("items", []))
            if len(devices) >= total_devices:
                break
            next += 1

        return devices

    @staticmethod
    def get_devices(
        central_conn, filter_str=None, sort=None, limit=DEVICE_LIMIT, next=1
    ):
        """
        Retrieve a single page of devices with optional filtering and sorting. This response retrieves a list of network devices that are onboarded and currently being monitored.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/devices`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next (int, optional): Pagination cursor for next page of resources (default is 1).

        Returns:
            (dict): API response from the device endpoint (typically contains 'items', 'total', and 'next').
        """
        params = {
            "limit": limit,
            "next": next,
            "filter": filter_str,
            "sort": sort,
        }

        path = MONITOR_TYPE
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_all_device_inventory(
        central_conn,
        filter_str=None,
        sort=None,
        site_assigned=None,
    ):
        """
        Retrieve all devices from the account, including devices that are not yet onboarded to new Central.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            site_assigned (str|None, optional): Filter by site-assigned status.
        Returns:
            (list[dict]): Processed list of all devices from inventory.
        """
        devices = []
        total_devices = None
        next_int = 1
        while True:
            response = MonitoringDevices.get_device_inventory(
                central_conn,
                filter_str=filter_str,
                sort=sort,
                site_assigned=site_assigned,
                limit=DEVICE_LIMIT,
                next=next_int,
            )
            if total_devices is None:
                total_devices = response.get("total", 0)
            devices.extend(response.get("items", []))
            if len(devices) == total_devices:
                break
            next_int += 1

        return devices

    @staticmethod
    def get_device_inventory(
        central_conn,
        filter_str=None,
        sort=None,
        site_assigned=None,
        limit=DEVICE_LIMIT,
        next=1,
    ):
        """
        Retrieve device data from device inventory API response. This API includes devices yet to be onboarded, as well as those already onboarded and currently being monitored.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/device-inventory`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            site_assigned (str|None, optional): Filter by site-assigned status. Supported values are "ASSIGNED", "UNASSIGNED"
            limit (int, optional): Number of entries to return (default is 100).
            next (int, optional): Pagination cursor for next page of resources (default is 1).

        Returns:
            (dict): Raw API response containing device inventory per site.

        """
        params = {
            "limit": limit,
            "next": next,
            "filter": filter_str,
            "sort": sort,
            "site-assigned": site_assigned,
        }
        path = "device-inventory"
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def delete_device(central_conn, serial_number):
        """
        Delete a device from Central Monitoring (device must be OFFLINE).

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device to delete.

        Returns:
            (tuple(bool, dict)): (True, API response) on success.

        Raises:
            ParameterError: If serial_number is missing or not a string.
            Exception: If delete API returns a non-200 response.

        """
        if not serial_number or not isinstance(serial_number, str):
            raise ParameterError(
                "serial_number is required and must be a string"
            )

        path = f"{MONITOR_TYPE}/{serial_number}"

        resp = central_conn.command("DELETE", path)

        if resp["code"] != 200:
            raise Exception(
                f"Error deleting device from {path}: {resp['code']} - {resp['msg']}"
            )

        return True, resp
