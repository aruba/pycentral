from ..utils.monitoring_utils import execute_get
from ..exceptions import ParameterError

LOCATION_LIMIT = 100


class LocationServices:

    @staticmethod
    def get_device_locations(central_conn, filter_str=None, sort=None, limit=LOCATION_LIMIT, next_page=1):
        """
        Retrieve location data for all devices.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1alpha2/device-locations`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Max results (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response with device location items.

        Raises:
            ParameterError: If limit or next_page invalid.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > LOCATION_LIMIT:
            raise ParameterError(f"limit cannot exceed {LOCATION_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {"filter": filter_str, "sort": sort, "limit": limit, "next": next_page}
        return execute_get(central_conn, endpoint="device-locations", params=params, version="v1alpha2")

    @staticmethod
    def get_all_device_locations(central_conn, filter_str=None, sort=None):
        """Retrieve all device locations, handling pagination.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.

        Returns:
            (list[dict]): List of all device location items.
        """
        locations = []
        total = None
        next_page = 1
        while True:
            resp = LocationServices.get_device_locations(
                central_conn, filter_str=filter_str, sort=sort,
                limit=LOCATION_LIMIT, next_page=next_page
            )
            if total is None:
                total = resp.get("total", 0)
            locations.extend(resp.get("items", []))
            if len(locations) >= total:
                break
            next_val = resp.get("next")
            if not next_val:
                break
            next_page = int(next_val)
        return locations

    @staticmethod
    def get_location_by_id(central_conn, location_id):
        """
        Retrieve a location by its ID.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1alpha2/locations/{location_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            location_id (str): Location identifier.

        Returns:
            (dict): Location details.

        Raises:
            ParameterError: If location_id missing.
        """
        if not location_id or not isinstance(location_id, str):
            raise ParameterError("location_id is required and must be a string")
        return execute_get(central_conn, endpoint=f"locations/{location_id}", version="v1alpha2")

    @staticmethod
    def get_device_detailed_location(central_conn, serial_number):
        """
        Retrieve detailed location information for a specific device.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1alpha2/devices/{serial_number}/location`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Device serial number.

        Returns:
            (dict): Detailed location information.

        Raises:
            ParameterError: If serial_number missing.
        """
        if not serial_number or not isinstance(serial_number, str):
            raise ParameterError("serial_number is required and must be a string")
        return execute_get(central_conn, endpoint=f"devices/{serial_number}/location", version="v1alpha2")

    @staticmethod
    def get_ap_ranging_scans(central_conn, serial_number, filter_str=None, sort=None, limit=LOCATION_LIMIT, next_page=1):
        """
        Retrieve ranging scan list for an AP.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1alpha2/aps/{serial_number}/ranging-scans`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): AP serial number.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Max results (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response with ranging scan items.

        Raises:
            ParameterError: If serial_number missing or limit/next_page invalid.
        """
        if not serial_number or not isinstance(serial_number, str):
            raise ParameterError("serial_number is required and must be a string")
        if limit > LOCATION_LIMIT:
            raise ParameterError(f"limit cannot exceed {LOCATION_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {"filter": filter_str, "sort": sort, "limit": limit, "next": next_page}
        return execute_get(central_conn, endpoint=f"aps/{serial_number}/ranging-scans",
                           params=params, version="v1alpha2")

    @staticmethod
    def get_ap_ranging_scan(central_conn, serial_number, scan_id):
        """
        Retrieve a specific ranging scan for an AP.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1alpha2/aps/{serial_number}/ranging-scans/{scan_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): AP serial number.
            scan_id (str): Ranging scan identifier.

        Returns:
            (dict): Ranging scan details.

        Raises:
            ParameterError: If serial_number or scan_id missing.
        """
        if not serial_number or not isinstance(serial_number, str):
            raise ParameterError("serial_number is required and must be a string")
        if not scan_id or not isinstance(scan_id, str):
            raise ParameterError("scan_id is required and must be a string")
        return execute_get(central_conn, endpoint=f"aps/{serial_number}/ranging-scans/{scan_id}",
                           version="v1alpha2")

    @staticmethod
    def list_asset_tag_data(central_conn, filter_str=None, sort=None, limit=LOCATION_LIMIT, next_page=1):
        """
        Retrieve asset tag location data.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1alpha2/asset-tags`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Max results (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response with asset tag items.

        Raises:
            ParameterError: If limit or next_page invalid.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > LOCATION_LIMIT:
            raise ParameterError(f"limit cannot exceed {LOCATION_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {"filter": filter_str, "sort": sort, "limit": limit, "next": next_page}
        return execute_get(central_conn, endpoint="asset-tags", params=params, version="v1alpha2")
