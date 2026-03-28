from ..utils.monitoring_utils import execute_get
from ..utils.url_utils import generate_url
from ..exceptions import ParameterError

FLOOR_LIMIT = 100


class FloorPlan:
    """Manage floor plans, buildings, walls, zones, and device placement."""

    # -------------------------------------------------------------------------
    # Buildings
    # -------------------------------------------------------------------------

    @staticmethod
    def get_buildings(central_conn, filter_str=None, sort=None, limit=FLOOR_LIMIT, next_page=1):
        """
        Retrieve a list of buildings.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/buildings`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Max results per page (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response with building items.

        Raises:
            ParameterError: If central_conn is None or limit/next_page invalid.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > FLOOR_LIMIT:
            raise ParameterError(f"limit cannot exceed {FLOOR_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {"filter": filter_str, "sort": sort, "limit": limit, "next": next_page}
        return execute_get(central_conn, endpoint="buildings", params=params)

    @staticmethod
    def update_building(central_conn, building_id, **kwargs):
        """
        Update a building.

        This method makes an API call to the following endpoint - `PUT network-monitoring/v1/buildings/{building_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            building_id (str): Building identifier.
            **kwargs: Fields to update per API spec (e.g. name, address, campus_id).

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If building_id is missing.
        """
        FloorPlan._validate_str_param(building_id, "building_id")
        path = generate_url(f"buildings/{building_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="PUT", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(f"Error updating building {building_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def delete_building(central_conn, building_id):
        """
        Delete a building.

        This method makes an API call to the following endpoint - `DELETE network-monitoring/v1/buildings/{building_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            building_id (str): Building identifier.

        Returns:
            (bool): True if deleted successfully.

        Raises:
            ParameterError: If building_id is missing.
        """
        FloorPlan._validate_str_param(building_id, "building_id")
        path = generate_url(f"buildings/{building_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="DELETE", api_path=path)
        if resp["code"] != 200:
            raise Exception(f"Error deleting building {building_id}: {resp['code']} - {resp['msg']}")
        return True

    # -------------------------------------------------------------------------
    # Floors
    # -------------------------------------------------------------------------

    @staticmethod
    def create_floor(central_conn, building_id, floor_name, floor_number, **kwargs):
        """
        Create a new floor.

        This method makes an API call to the following endpoint - `POST network-monitoring/v1/floors`

        Args:
            central_conn (NewCentralBase): Central connection object.
            building_id (str): Building identifier to attach the floor to.
            floor_name (str): Name of the floor.
            floor_number (int): Floor number.
            **kwargs: Additional floor fields per API spec (e.g. dimensions, units).

        Returns:
            (dict): Created floor response.

        Raises:
            ParameterError: If building_id, floor_name, or floor_number is missing.
        """
        FloorPlan._validate_str_param(building_id, "building_id")
        FloorPlan._validate_str_param(floor_name, "floor_name")
        if floor_number is None:
            raise ParameterError("floor_number is required")
        body = {"building_id": building_id, "floor_name": floor_name, "floor_number": floor_number, **kwargs}
        path = generate_url("floors", "monitoring", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data=body)
        if resp["code"] not in (200, 201):
            raise Exception(f"Error creating floor: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def get_floor(central_conn, floor_id):
        """
        Retrieve floor summary.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/{floor_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.

        Returns:
            (dict): Floor details.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        return execute_get(central_conn, endpoint=f"floors/{floor_id}")

    @staticmethod
    def delete_floor(central_conn, floor_id):
        """
        Delete a floor.

        This method makes an API call to the following endpoint - `DELETE network-monitoring/v1/floors/{floor_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.

        Returns:
            (bool): True if deleted successfully.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        path = generate_url(f"floors/{floor_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="DELETE", api_path=path)
        if resp["code"] != 200:
            raise Exception(f"Error deleting floor {floor_id}: {resp['code']} - {resp['msg']}")
        return True

    @staticmethod
    def update_floor_map(central_conn, floor_id, **kwargs):
        """
        Update floor map configuration.

        This method makes an API call to the following endpoint - `PUT network-monitoring/v1/floors/{floor_id}/map`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            **kwargs: Map fields per API spec (e.g. width, length, units, rotation).

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        path = generate_url(f"floors/{floor_id}/map", "monitoring", "v1")
        resp = central_conn.command(api_method="PUT", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(f"Error updating floor map {floor_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def scale_floor_map(central_conn, floor_id, **kwargs):
        """
        Scale the floor map.

        This method makes an API call to the following endpoint - `POST network-monitoring/v1/floors/{floor_id}/scale`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            **kwargs: Scale parameters per API spec (e.g. pixels_per_unit, scale_type).

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        path = generate_url(f"floors/{floor_id}/scale", "monitoring", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data=kwargs)
        if resp["code"] not in (200, 201):
            raise Exception(f"Error scaling floor map {floor_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def import_floors(central_conn, floor_data):
        """
        Import floors in bulk.

        This method makes an API call to the following endpoint - `POST network-monitoring/v1/floors/import`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_data (dict): Import payload per API spec.

        Returns:
            (dict): API response including a job_id for status polling.

        Raises:
            ParameterError: If floor_data is missing.
        """
        if not floor_data or not isinstance(floor_data, dict):
            raise ParameterError("floor_data is required and must be a dict")
        path = generate_url("floors/import", "monitoring", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data=floor_data)
        if resp["code"] not in (200, 201, 202):
            raise Exception(f"Error importing floors: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def get_import_status(central_conn, job_id):
        """
        Get the status of a floor import job.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/import/{job_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            job_id (str): Import job identifier.

        Returns:
            (dict): Import job status.

        Raises:
            ParameterError: If job_id is missing.
        """
        FloorPlan._validate_str_param(job_id, "job_id")
        return execute_get(central_conn, endpoint=f"floors/import/{job_id}")

    # -------------------------------------------------------------------------
    # Wall Types
    # -------------------------------------------------------------------------

    @staticmethod
    def get_wall_types(central_conn):
        """
        Retrieve all wall types.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/wall-types`

        Args:
            central_conn (NewCentralBase): Central connection object.

        Returns:
            (dict): Wall types response.

        Raises:
            ParameterError: If central_conn is None.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        return execute_get(central_conn, endpoint="wall-types")

    @staticmethod
    def create_wall_types(central_conn, wall_types):
        """
        Create one or more wall types.

        This method makes an API call to the following endpoint - `POST network-monitoring/v1/wall-types`

        Args:
            central_conn (NewCentralBase): Central connection object.
            wall_types (list[dict]): List of wall type objects per API spec.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If wall_types is not a non-empty list.
        """
        if not wall_types or not isinstance(wall_types, list):
            raise ParameterError("wall_types must be a non-empty list")
        path = generate_url("wall-types", "monitoring", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data={"wall_types": wall_types})
        if resp["code"] not in (200, 201):
            raise Exception(f"Error creating wall types: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def update_wall_type(central_conn, type_id, **kwargs):
        """
        Update a wall type.

        This method makes an API call to the following endpoint - `PUT network-monitoring/v1/wall-types/{type_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            type_id (str): Wall type identifier.
            **kwargs: Fields to update per API spec.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If type_id is missing.
        """
        FloorPlan._validate_str_param(type_id, "type_id")
        path = generate_url(f"wall-types/{type_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="PUT", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(f"Error updating wall type {type_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def delete_wall_type(central_conn, type_id):
        """
        Delete a wall type.

        This method makes an API call to the following endpoint - `DELETE network-monitoring/v1/wall-types/{type_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            type_id (str): Wall type identifier.

        Returns:
            (bool): True if deleted successfully.

        Raises:
            ParameterError: If type_id is missing.
        """
        FloorPlan._validate_str_param(type_id, "type_id")
        path = generate_url(f"wall-types/{type_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="DELETE", api_path=path)
        if resp["code"] != 200:
            raise Exception(f"Error deleting wall type {type_id}: {resp['code']} - {resp['msg']}")
        return True

    # -------------------------------------------------------------------------
    # Walls
    # -------------------------------------------------------------------------

    @staticmethod
    def get_walls(central_conn, floor_id):
        """
        Retrieve walls for a floor.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/{floor_id}/walls`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.

        Returns:
            (dict): Walls response.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        return execute_get(central_conn, endpoint=f"floors/{floor_id}/walls")

    @staticmethod
    def create_walls(central_conn, floor_id, walls):
        """
        Create walls on a floor.

        This method makes an API call to the following endpoint - `POST network-monitoring/v1/floors/{floor_id}/walls`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            walls (list[dict]): List of wall objects per API spec.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id missing or walls is not a non-empty list.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        if not walls or not isinstance(walls, list):
            raise ParameterError("walls must be a non-empty list")
        path = generate_url(f"floors/{floor_id}/walls", "monitoring", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data={"walls": walls})
        if resp["code"] not in (200, 201):
            raise Exception(f"Error creating walls on floor {floor_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def update_wall(central_conn, floor_id, wall_id, **kwargs):
        """
        Update a wall on a floor.

        This method makes an API call to the following endpoint - `PUT network-monitoring/v1/floors/{floor_id}/walls/{wall_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            wall_id (str): Wall identifier.
            **kwargs: Fields to update per API spec.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id or wall_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        FloorPlan._validate_str_param(wall_id, "wall_id")
        path = generate_url(f"floors/{floor_id}/walls/{wall_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="PUT", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(f"Error updating wall {wall_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def delete_wall(central_conn, floor_id, wall_id):
        """
        Delete a wall from a floor.

        This method makes an API call to the following endpoint - `DELETE network-monitoring/v1/floors/{floor_id}/walls/{wall_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            wall_id (str): Wall identifier.

        Returns:
            (bool): True if deleted successfully.

        Raises:
            ParameterError: If floor_id or wall_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        FloorPlan._validate_str_param(wall_id, "wall_id")
        path = generate_url(f"floors/{floor_id}/walls/{wall_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="DELETE", api_path=path)
        if resp["code"] != 200:
            raise Exception(f"Error deleting wall {wall_id}: {resp['code']} - {resp['msg']}")
        return True

    # -------------------------------------------------------------------------
    # Zones
    # -------------------------------------------------------------------------

    @staticmethod
    def get_zones(central_conn, floor_id):
        """
        Retrieve zones for a floor.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/{floor_id}/zones`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.

        Returns:
            (dict): Zones response.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        return execute_get(central_conn, endpoint=f"floors/{floor_id}/zones")

    @staticmethod
    def create_zones(central_conn, floor_id, zones):
        """
        Create zones on a floor.

        This method makes an API call to the following endpoint - `POST network-monitoring/v1/floors/{floor_id}/zones`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            zones (list[dict]): List of zone objects per API spec.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id missing or zones is not a non-empty list.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        if not zones or not isinstance(zones, list):
            raise ParameterError("zones must be a non-empty list")
        path = generate_url(f"floors/{floor_id}/zones", "monitoring", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data={"zones": zones})
        if resp["code"] not in (200, 201):
            raise Exception(f"Error creating zones on floor {floor_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def update_zone(central_conn, floor_id, zone_id, **kwargs):
        """
        Update a zone on a floor.

        This method makes an API call to the following endpoint - `PUT network-monitoring/v1/floors/{floor_id}/zones/{zone_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            zone_id (str): Zone identifier.
            **kwargs: Fields to update per API spec.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id or zone_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        FloorPlan._validate_str_param(zone_id, "zone_id")
        path = generate_url(f"floors/{floor_id}/zones/{zone_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="PUT", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(f"Error updating zone {zone_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def delete_zone(central_conn, floor_id, zone_id):
        """
        Delete a zone from a floor.

        This method makes an API call to the following endpoint - `DELETE network-monitoring/v1/floors/{floor_id}/zones/{zone_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            zone_id (str): Zone identifier.

        Returns:
            (bool): True if deleted successfully.

        Raises:
            ParameterError: If floor_id or zone_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        FloorPlan._validate_str_param(zone_id, "zone_id")
        path = generate_url(f"floors/{floor_id}/zones/{zone_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="DELETE", api_path=path)
        if resp["code"] != 200:
            raise Exception(f"Error deleting zone {zone_id}: {resp['code']} - {resp['msg']}")
        return True

    # -------------------------------------------------------------------------
    # Device Placement
    # -------------------------------------------------------------------------

    @staticmethod
    def get_placed_devices(central_conn, floor_id, filter_str=None):
        """
        Retrieve devices placed on a floor.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/{floor_id}/devices`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            filter_str (str, optional): OData filter expression.

        Returns:
            (dict): Placed devices response.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        params = {"filter": filter_str}
        return execute_get(central_conn, endpoint=f"floors/{floor_id}/devices", params=params)

    @staticmethod
    def place_devices(central_conn, floor_id, devices):
        """
        Place devices on a floor.

        This method makes an API call to the following endpoint - `POST network-monitoring/v1/floors/{floor_id}/devices`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            devices (list[dict]): List of device placement objects per API spec.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id missing or devices is not a non-empty list.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        if not devices or not isinstance(devices, list):
            raise ParameterError("devices must be a non-empty list")
        path = generate_url(f"floors/{floor_id}/devices", "monitoring", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data={"devices": devices})
        if resp["code"] not in (200, 201):
            raise Exception(f"Error placing devices on floor {floor_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def remove_devices(central_conn, floor_id, device_ids):
        """
        Remove devices from a floor.

        This method makes an API call to the following endpoint - `DELETE network-monitoring/v1/floors/{floor_id}/devices`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            device_ids (list[str]): List of device IDs to remove.

        Returns:
            (bool): True if removed successfully.

        Raises:
            ParameterError: If floor_id missing or device_ids not a non-empty list.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        if not device_ids or not isinstance(device_ids, list):
            raise ParameterError("device_ids must be a non-empty list")
        path = generate_url(f"floors/{floor_id}/devices", "monitoring", "v1")
        resp = central_conn.command(api_method="DELETE", api_path=path,
                                    api_data={"device_ids": device_ids})
        if resp["code"] != 200:
            raise Exception(f"Error removing devices from floor {floor_id}: {resp['code']} - {resp['msg']}")
        return True

    @staticmethod
    def change_device_assignment(central_conn, floor_id, device_id, **kwargs):
        """
        Change a device's placement or assignment on a floor.

        This method makes an API call to the following endpoint - `PATCH network-monitoring/v1/floors/{floor_id}/devices/{device_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            device_id (str): Device identifier.
            **kwargs: Placement fields per API spec (e.g. x, y, orientation).

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If floor_id or device_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        FloorPlan._validate_str_param(device_id, "device_id")
        path = generate_url(f"floors/{floor_id}/devices/{device_id}", "monitoring", "v1")
        resp = central_conn.command(api_method="PATCH", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(f"Error changing device {device_id} assignment: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def get_associated_devices(central_conn, floor_id):
        """
        Retrieve devices associated with a floor (not necessarily placed).

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/{floor_id}/associated-devices`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.

        Returns:
            (dict): Associated devices response.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        return execute_get(central_conn, endpoint=f"floors/{floor_id}/associated-devices")

    # -------------------------------------------------------------------------
    # Heatmaps
    # -------------------------------------------------------------------------

    @staticmethod
    def get_heatmap(central_conn, floor_id, heatmap_type=None):
        """
        Retrieve heatmap data for a floor.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/{floor_id}/heatmap`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.
            heatmap_type (str, optional): Type of heatmap (e.g. 'rssi', 'snr').

        Returns:
            (dict): Heatmap data.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        params = {"type": heatmap_type} if heatmap_type else {}
        return execute_get(central_conn, endpoint=f"floors/{floor_id}/heatmap", params=params)

    @staticmethod
    def get_channel_occupancy_heatmap(central_conn, floor_id):
        """
        Retrieve channel occupancy heatmap for a floor.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/floors/{floor_id}/channel-occupancy-heatmap`

        Args:
            central_conn (NewCentralBase): Central connection object.
            floor_id (str): Floor identifier.

        Returns:
            (dict): Channel occupancy heatmap data.

        Raises:
            ParameterError: If floor_id is missing.
        """
        FloorPlan._validate_str_param(floor_id, "floor_id")
        return execute_get(central_conn, endpoint=f"floors/{floor_id}/channel-occupancy-heatmap")

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _validate_str_param(value, name):
        """
        Validate that a parameter is a non-empty string.

        Args:
            value: Value to validate.
            name (str): Parameter name for the error message.

        Raises:
            ParameterError: If value is not a non-empty string.

        Note:
            Internal SDK function
        """
        if not value or not isinstance(value, str):
            raise ParameterError(f"{name} is required and must be a non-empty string")
