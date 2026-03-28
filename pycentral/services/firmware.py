# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.url_utils import generate_url
from ..exceptions import ParameterError

FIRMWARE_DETAILS_ENDPOINT = "firmware-details"
FIRMWARE_LIMIT = 100


class FirmwareService:
    @staticmethod
    def get_firmware_details(central_conn, filter_str=None, sort=None, limit=100, next_page=1):
        """Retrieve firmware details list.

        This method makes an API call to the following endpoint - `GET network-services/v1/firmware-details`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Max results per page (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response with firmware details items, including fields such as
                firmware_version, upgrade_status, recommended_version,
                firmware_classification, and last_upgraded_timestamp.

        Raises:
            ParameterError: If central_conn is None, limit exceeds 100, or next_page is
                less than 1.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > FIRMWARE_LIMIT:
            raise ParameterError(f"limit cannot exceed {FIRMWARE_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")

        params = {
            "filter": filter_str,
            "sort": sort,
            "limit": limit,
            "next": next_page,
        }

        path = generate_url(FIRMWARE_DETAILS_ENDPOINT, "services", "v1")
        resp = central_conn.command("GET", path, api_params=params)
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving firmware details from {path}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def get_all_firmware_details(central_conn, filter_str=None, sort=None):
        """Retrieve all firmware details, handling pagination automatically.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.

        Returns:
            (list): All firmware detail items across all pages.

        Raises:
            ParameterError: If central_conn is None.
        """
        items = []
        total = None
        next_page = 1
        while True:
            resp = FirmwareService.get_firmware_details(
                central_conn,
                filter_str=filter_str,
                sort=sort,
                limit=FIRMWARE_LIMIT,
                next_page=next_page,
            )
            if total is None:
                total = resp.get("total", 0)

            items.extend(resp.get("items", []))

            if total is not None and len(items) >= total:
                break

            next_val = resp.get("next")
            if not next_val:
                break
            next_page = int(next_val)
        return items
