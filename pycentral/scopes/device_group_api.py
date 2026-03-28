# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.url_utils import generate_url
from ..exceptions import ParameterError

DEVICE_COLLECTION_ENDPOINT = "device-collections"
DEVICE_GROUP_LIMIT = 100


class DeviceGroupAPI:
    """Standalone API class for device group (device-collection) write operations."""

    @staticmethod
    def get_device_groups(
        central_conn, filter_str=None, sort=None, limit=DEVICE_GROUP_LIMIT, next_page=1
    ):
        """Retrieve a page of device groups.

        This method makes an API call to the following endpoint -
        ``GET network-config/v1alpha1/device-collections``

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Number of entries to return per page (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response body containing ``items``, ``total``, and ``next``
                fields.

        Raises:
            ParameterError: If ``central_conn`` is None, ``limit`` exceeds
                ``DEVICE_GROUP_LIMIT``, or ``next_page`` is less than 1.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > DEVICE_GROUP_LIMIT:
            raise ParameterError(f"limit cannot exceed {DEVICE_GROUP_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")

        params = {
            "filter": filter_str,
            "sort": sort,
            "limit": limit,
            "next": next_page,
        }

        path = generate_url(DEVICE_COLLECTION_ENDPOINT, "configuration", "latest")
        resp = central_conn.command("GET", path, api_params=params)
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving device groups from {path}: "
                f"{resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def get_all_device_groups(central_conn, filter_str=None, sort=None):
        """Retrieve all device groups, handling pagination automatically.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.

        Returns:
            (list[dict]): All device group items across all pages.

        Raises:
            ParameterError: If ``central_conn`` is None.
        """
        items = []
        total = None
        next_page = 1
        while True:
            resp = DeviceGroupAPI.get_device_groups(
                central_conn,
                filter_str=filter_str,
                sort=sort,
                limit=DEVICE_GROUP_LIMIT,
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

    @staticmethod
    def create_device_group(central_conn, name, description=None):
        """Create a new device group.

        This method makes an API call to the following endpoint -
        ``POST network-config/v1alpha1/device-collections``

        Args:
            central_conn (NewCentralBase): Central connection object.
            name (str): Name of the device group.
            description (str, optional): Description of the device group.

        Returns:
            (dict): API response body.

        Raises:
            ParameterError: If ``central_conn`` is None or ``name`` is missing.
            Exception: If the API call fails.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not name:
            raise ParameterError("name is required and cannot be empty")

        body = {"scopeName": name}
        if description:
            body["description"] = description

        path = generate_url(DEVICE_COLLECTION_ENDPOINT, "configuration", "latest")
        resp = central_conn.command("POST", path, api_data=body)
        if resp["code"] not in (200, 201):
            raise Exception(
                f"Error creating device group via {path}: "
                f"{resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def update_device_group(central_conn, scope_id, name=None, description=None):
        """Update a device group.

        This method makes an API call to the following endpoint -
        ``PUT network-config/v1alpha1/device-collections/{scope_id}``

        Args:
            central_conn (NewCentralBase): Central connection object.
            scope_id (str | int): Scope ID of the device group to update.
            name (str, optional): New name for the device group.
            description (str, optional): New description for the device group.

        Returns:
            (dict): API response body.

        Raises:
            ParameterError: If ``central_conn`` or ``scope_id`` is missing, or if
                neither ``name`` nor ``description`` is provided.
            Exception: If the API call fails.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if scope_id is None:
            raise ParameterError("scope_id is required")
        if name is None and description is None:
            raise ParameterError(
                "At least one of 'name' or 'description' must be provided"
            )

        body = {}
        if name is not None:
            body["scopeName"] = name
        if description is not None:
            body["description"] = description

        endpoint = f"{DEVICE_COLLECTION_ENDPOINT}/{scope_id}"
        path = generate_url(endpoint, "configuration", "latest")
        resp = central_conn.command("PUT", path, api_data=body)
        if resp["code"] not in (200, 201):
            raise Exception(
                f"Error updating device group {scope_id} via {path}: "
                f"{resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def delete_device_group(central_conn, scope_id):
        """Delete a device group by scope ID.

        This method makes an API call to the following endpoint -
        ``DELETE network-config/v1alpha1/device-collections/{scope_id}``

        Args:
            central_conn (NewCentralBase): Central connection object.
            scope_id (str | int): Scope ID of the device group to delete.

        Returns:
            (dict): API response body.

        Raises:
            ParameterError: If ``central_conn`` or ``scope_id`` is missing.
            Exception: If the API call fails.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if scope_id is None:
            raise ParameterError("scope_id is required")

        endpoint = f"{DEVICE_COLLECTION_ENDPOINT}/{scope_id}"
        path = generate_url(endpoint, "configuration", "latest")
        resp = central_conn.command("DELETE", path)
        if resp["code"] != 200:
            raise Exception(
                f"Error deleting device group {scope_id} via {path}: "
                f"{resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def delete_device_groups_bulk(central_conn, scope_ids):
        """Bulk delete device groups.

        This method makes an API call to the following endpoint -
        ``DELETE network-config/v1alpha1/device-collections``

        Args:
            central_conn (NewCentralBase): Central connection object.
            scope_ids (list[str | int]): List of scope IDs to delete.

        Returns:
            (dict): API response body.

        Raises:
            ParameterError: If ``central_conn`` is None or ``scope_ids`` is empty.
            Exception: If the API call fails.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not scope_ids:
            raise ParameterError("scope_ids must be a non-empty list")

        params = {"scopeIds": [str(sid) for sid in scope_ids]}
        path = generate_url(DEVICE_COLLECTION_ENDPOINT, "configuration", "latest")
        resp = central_conn.command("DELETE", path, api_params=params)
        if resp["code"] != 200:
            raise Exception(
                f"Error bulk-deleting device groups via {path}: "
                f"{resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def add_devices(central_conn, scope_id, serial_numbers):
        """Add devices to a device group.

        This method makes an API call to the following endpoint -
        ``POST network-config/v1alpha1/device-collections/{scope_id}/devices``

        Args:
            central_conn (NewCentralBase): Central connection object.
            scope_id (str | int): Scope ID of the device group.
            serial_numbers (list[str]): Serial numbers of devices to add.

        Returns:
            (dict): API response body.

        Raises:
            ParameterError: If ``central_conn`` or ``scope_id`` is missing, or if
                ``serial_numbers`` is empty.
            Exception: If the API call fails.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if scope_id is None:
            raise ParameterError("scope_id is required")
        if not serial_numbers:
            raise ParameterError("serial_numbers must be a non-empty list")

        body = {"serialNumbers": serial_numbers}
        endpoint = f"{DEVICE_COLLECTION_ENDPOINT}/{scope_id}/devices"
        path = generate_url(endpoint, "configuration", "latest")
        resp = central_conn.command("POST", path, api_data=body)
        if resp["code"] not in (200, 201):
            raise Exception(
                f"Error adding devices to device group {scope_id} via {path}: "
                f"{resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def remove_devices(central_conn, scope_id, serial_numbers):
        """Remove devices from a device group.

        This method makes an API call to the following endpoint -
        ``DELETE network-config/v1alpha1/device-collections/{scope_id}/devices``

        Args:
            central_conn (NewCentralBase): Central connection object.
            scope_id (str | int): Scope ID of the device group.
            serial_numbers (list[str]): Serial numbers of devices to remove.

        Returns:
            (dict): API response body.

        Raises:
            ParameterError: If ``central_conn`` or ``scope_id`` is missing, or if
                ``serial_numbers`` is empty.
            Exception: If the API call fails.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if scope_id is None:
            raise ParameterError("scope_id is required")
        if not serial_numbers:
            raise ParameterError("serial_numbers must be a non-empty list")

        params = {"serialNumbers": serial_numbers}
        endpoint = f"{DEVICE_COLLECTION_ENDPOINT}/{scope_id}/devices"
        path = generate_url(endpoint, "configuration", "latest")
        resp = central_conn.command("DELETE", path, api_params=params)
        if resp["code"] != 200:
            raise Exception(
                f"Error removing devices from device group {scope_id} via {path}: "
                f"{resp['code']} - {resp['msg']}"
            )
        return resp["msg"]
