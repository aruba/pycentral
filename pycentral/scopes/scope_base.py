# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_maps import create_config_assignment, delete_config_assignment
from ..exceptions import ParameterError
from ..utils.profile_utils import _resolve_device_function
from ..utils.scope_utils import (
    fetch_attribute,
)


class ScopeBase:
    """Base class for all scope elements, such as Site, Site_Collection, and Device.

    Provides common functionality like:
      - Returning the object's ID or name.
      - Assigning and unassigning profiles.
    """

    def get_id(self):
        """Fetches the ID of the scope element.

        Returns:
            (int): ID of the scope element
        """
        return fetch_attribute(self, "id")

    def get_name(self):
        """Fetches the name of the scope element.

        Returns:
            (str): Name of the scope element
        """
        return fetch_attribute(self, "name")

    def get_type(self):
        """Fetches the type of the scope element.

        Returns:
            (str): Type of the scope element (e.g., 'site', 'site_collection', 'device')
        """
        return fetch_attribute(self, "type")

    def assign_profile(
        self,
        profile_name,
        profile_persona=None,  # remove persona in 2.x
        *,
        device_function=None,
    ):
        """Assigns a profile to the scope via the config-assignments API.

        Args:
            profile_name (str): Profile resource string
                "<profile-type>/<profile-instance>", e.g. "layer2-vlan/100"
                (see Profiles.get_resource_str()).
            profile_persona (str, optional): Deprecated alias of device_function.
            device_function (str, optional): Device function of the profile,
                e.g. "CAMPUS_AP" or "ALL". Optional if assigning to a device
                (defaults to the device's config_persona). "ALL" depends on a
                Central feature flag and may be rejected; the API's error is logged.

        Returns:
            (bool): True if the profile assignment was successful, False otherwise

        Raises:
            ParameterError: If profile_name is not "<profile-type>/<profile-instance>"
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=profile_persona
        )
        return self._config_assignment("assign", profile_name, device_function)

    def unassign_profile(
        self,
        profile_name,
        profile_persona=None,  # remove persona in 2.x
        *,
        device_function=None,
    ):
        """Unassigns a profile from the scope via the config-assignments API.

        Args:
            profile_name (str): Profile resource string
                "<profile-type>/<profile-instance>", e.g. "layer2-vlan/100".
            profile_persona (str, optional): Deprecated alias of device_function.
            device_function (str, optional): Device function of the profile.
                Optional if unassigning from a device.

        Returns:
            (bool): True if the profile unassignment was successful, False otherwise

        Raises:
            ParameterError: If profile_name is not "<profile-type>/<profile-instance>"
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=profile_persona
        )
        return self._config_assignment(
            "unassign", profile_name, device_function
        )

    def _config_assignment(self, operation, profile_name, device_function):
        """Creates or deletes the config assignment of profile_name on this scope.

        Args:
            operation (str): "assign" or "unassign"
            profile_name (str): "<profile-type>/<profile-instance>"
            device_function (str or None): Device function of the profile

        Returns:
            (bool): True if successful, False otherwise
        """
        profile_type, _, profile_instance = (profile_name or "").partition("/")
        if not profile_type or not profile_instance:
            raise ParameterError(
                f"profile_name must be '<profile-type>/<profile-instance>', e.g. 'layer2-vlan/100', got {profile_name!r}"
            )
        device_function = self._resolve_scope_device_function(device_function)
        if device_function is None:
            return False
        if operation == "unassign" and any(
            p["resource"] == profile_name
            and p["device_function"] == device_function
            and p.get("object_type") == "LOCAL"
            for p in getattr(self, "assigned_profiles", [])
        ):
            self.central_conn.logger.error(
                f"'{profile_name}' is a local profile at this scope; it cannot be unassigned. Delete it with Profiles(..., local={{'scope_id': {self.get_id()}, 'device_function': '{device_function}'}}).delete() instead."
            )
            return False
        request = (
            create_config_assignment
            if operation == "assign"
            else delete_config_assignment
        )
        resp = request(
            self.central_conn,
            self.get_id(),
            device_function,
            profile_type,
            profile_instance,
        )
        if resp["code"] != 200:
            self.central_conn.logger.error(
                f"Unable to {operation} profile {profile_name} ({device_function}) for {self.get_name()}. Error message - {resp['msg']}"
            )
            return False
        self.central_conn.logger.info(
            f"Successfully {operation}ed profile {profile_name} ({device_function}) for {self.get_name()}"
        )
        record = self.add_profile if operation == "assign" else self.remove_profile
        record(name=profile_name, device_function=device_function)
        return True

    def _resolve_scope_device_function(self, device_function):
        """Validates and resolves the device function for this scope.

        Devices default to their config_persona; other scopes require one.

        Args:
            device_function (str or None): Device function to validate

        Returns:
            (str or None): Resolved device function or None if invalid
        """
        device_function = device_function or None
        if self.get_type() != "device":
            if device_function is None:
                self.central_conn.logger.error(
                    "Device function is required when assigning a profile to a scope other than device."
                )
            return device_function
        if not self.provisioned_status:
            self.central_conn.logger.error(
                "Device is currently configured via Classic Central only. Please provision the device to new Central before assigning/unassigning profile to device."
            )
            return None
        config_persona = getattr(self, "config_persona", None)
        if config_persona is None or device_function not in (
            None,
            config_persona,
        ):
            self.central_conn.logger.error(
                f"Invalid device function '{device_function}' for device. Device's current device function is {self.device_function} ({config_persona}). Leave device_function empty to use the device's current device function."
            )
            return None
        return config_persona

    def add_profile(
        self, name, persona=None, *, device_function=None, object_type="LIBRARY"
    ):  # remove persona in 2.x
        """Helper function that adds a profile to the assigned profiles of the scope in the SDK.

        Args:
            name (str): Profile resource string "<profile-type>/<profile-instance>"
            persona (str, optional): Deprecated alias of device_function.
            device_function (str): Device function of the profile
            object_type (str, optional): "LIBRARY" or "LOCAL"
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=persona
        )
        self.assigned_profiles.append(
            {
                "device_function": device_function,
                "persona": device_function,  # remove persona in 2.x
                "resource": name,
                "object_type": object_type,
            }
        )

    def remove_profile(
        self, name, persona=None, *, device_function=None
    ):  # remove persona in 2.x
        """Helper function that removes a profile from the assigned profiles of the scope in the SDK.

        Args:
            name (str): Profile resource string "<profile-type>/<profile-instance>"
            persona (str, optional): Deprecated alias of device_function.
            device_function (str): Device function of the profile

        Returns:
            (bool): True if the profile was successfully removed, False otherwise
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=persona
        )
        for index, element in enumerate(self.assigned_profiles):
            if (
                element["device_function"] == device_function
                and element["resource"] == name
            ):
                self.assigned_profiles.pop(index)
                return True
        return False
