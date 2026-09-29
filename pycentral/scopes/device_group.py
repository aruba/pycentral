from .scope_base import ScopeBase
from ..utils.scope_utils import rename_keys


API_ATTRIBUTE_MAPPING = {
    "deviceCount": "device_count",
    "id": "id",
    "scopeName": "name",
    "description": "description",
}

REQUIRED_ATTRIBUTES = ["name", "id"]


class Device_Group(ScopeBase):
    """This class holds device groups and all of its attributes & related methods."""

    def __init__(
        self, device_group_attributes=None, central_conn=None, from_api=False
    ):
        """Constructor for Device Group object.

        Args:
            device_group_attributes (dict, optional): Attributes of the Device Group
            central_conn (NewCentralBase, optional): Instance of NewCentralBase
                to establish connection to Central
            from_api (bool, optional): Boolean indicates if the device_group_attributes is from the
                Central API response

        Raises:
            Exception: If from_api is False (currently not supported)
        """
        self.materialized = from_api
        self.central_conn = central_conn
        self.type = "device_group"
        if from_api:
            # Rename keys if attributes are from API
            device_group_attributes = rename_keys(
                device_group_attributes, API_ATTRIBUTE_MAPPING
            )
            device_group_attributes["assigned_profiles"] = []
            device_group_attributes["devices"] = []
            for key, value in device_group_attributes.items():
                setattr(self, key, value)
        else:
            raise Exception(
                "Currently, Device Group requires attributes from API response to be created."
            )
