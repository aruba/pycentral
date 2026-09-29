# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from urllib.parse import quote

from ..exceptions import ParameterError
from ..utils import SCOPE_URLS, generate_url
from ..utils.constants import ALL_DEVICE_FUNCTIONS
from ..utils.profile_utils import _resolve_device_function, _warn_deprecated


def get_config_assignments(
    central_conn, scope_id=None, device_function=None, profile_type=None
):
    """Performs a GET call to retrieve configuration profile assignments.

    Args:
        central_conn (NewCentralBase): Established Central connection object
        scope_id (int or str, optional): Only return assignments of this scope
        device_function (str, optional): Only return assignments of this device function
        profile_type (str, optional): Only return assignments of this profile type,
            e.g. "layer2-vlan"

    Returns:
        (list): List of config assignment dicts with keys scope-id, scope-name,
            scope-type, device-function, profile-type and profile-instance.
            None on failure.
    """
    api_params = {
        "scope-id": scope_id,
        "device-function": device_function,
        "profile-type": profile_type,
    }
    api_params = {k: str(v) for k, v in api_params.items() if v is not None}
    resp = central_conn.command(
        api_method="GET",
        api_path=generate_url(SCOPE_URLS["CONFIG_ASSIGNMENTS"]),
        api_params=api_params or None,
    )
    if resp["code"] != 200:
        central_conn.logger.error(
            f"Unable to fetch config assignments. Error code - {resp['code']}.\n Error Description - {resp['msg']}"
        )
        return None
    return resp["msg"].get("config-assignment", [])


def get_scope_maps(central_conn):
    """Performs a GET call to retrieve the scope maps (deprecated scope-maps API).

    Unlike config-assignments, scope maps also list local profiles.

    Args:
        central_conn (NewCentralBase): Established Central connection object

    Returns:
        (list): List of scope map dicts with keys scope-id, scope-name, persona
            and resource ("<profile-type>/<profile-instance>"). None on failure.
    """
    resp = central_conn.command(
        api_method="GET", api_path=generate_url(SCOPE_URLS["SCOPE-MAPS"])
    )
    if resp["code"] != 200:
        central_conn.logger.error(
            f"Unable to fetch scope maps data. Error code - {resp['code']}.\n Error Description - {resp['msg']}"
        )
        return None
    return resp["msg"].get("scope-map", [])


def create_config_assignment(
    central_conn, scope_id, device_function, profile_type, profile_instance
):
    """Performs a POST call to assign a profile instance to a scope.

    "ALL" is sent unchanged. Whether Central accepts it depends on a feature
    flag; it may be rejected (400 "Based on feature flag, Persona is not
    allowed to map").

    Args:
        central_conn (NewCentralBase): Established Central connection object
        scope_id (int or str): ID of the scope
        device_function (str): Device function, e.g. "CAMPUS_AP" or "ALL"
        profile_type (str): Profile type, e.g. "layer2-vlan"
        profile_instance (str or int): Profile instance name, e.g. "100"

    Returns:
        (dict): Response of the POST call
    """
    api_data = {
        "config-assignment": [
            {
                "scope-id": str(scope_id),
                "device-function": device_function,
                "profile-type": profile_type,
                "profile-instance": str(profile_instance),
            }
        ]
    }
    return central_conn.command(
        api_method="POST",
        api_path=generate_url(SCOPE_URLS["CONFIG_ASSIGNMENTS"]),
        api_data=api_data,
    )


def delete_config_assignment(
    central_conn, scope_id, device_function, profile_type, profile_instance
):
    """Performs a DELETE call to unassign a profile instance from a scope.

    "ALL" is sent unchanged. Whether Central accepts it depends on a feature
    flag; it may be rejected (400 "Based on feature flag, Persona is not
    allowed to map").

    Args:
        central_conn (NewCentralBase): Established Central connection object
        scope_id (int or str): ID of the scope
        device_function (str): Device function, e.g. "CAMPUS_AP" or "ALL"
        profile_type (str): Profile type, e.g. "layer2-vlan"
        profile_instance (str or int): Profile instance name, e.g. "100"

    Returns:
        (dict): Response of the DELETE call
    """
    api_path = generate_url(SCOPE_URLS["CONFIG_ASSIGNMENTS"]) + "/" + "/".join(
        quote(str(s), safe="")
        for s in (scope_id, device_function, profile_type, profile_instance)
    )
    return central_conn.command(api_method="DELETE", api_path=api_path)


class ScopeMaps:
    """Deprecated: use get_config_assignments, create_config_assignment and
    delete_config_assignment (config-assignments API) instead."""

    def __init__(self):
        _warn_deprecated(
            "ScopeMaps (scope-maps API) is deprecated; use "
            "pycentral.scopes.scope_maps.get_config_assignments, "
            "create_config_assignment and delete_config_assignment "
            "(config-assignments API) instead."
        )

    def get(self, central_conn):
        """Perform a GET call to retrieve data for the Global Scope Map.

        Args:
            central_conn (NewCentralBase): Established Central connection object

        Returns:
            (list): List of scope map dictionaries if success, empty list otherwise
        """
        scope_maps_list = get_scope_maps(central_conn) or []
        for mapping in scope_maps_list:
            mapping["scope-name"] = int(mapping["scope-name"])
        return scope_maps_list

    def get_scope_assigned_profiles(self, central_conn, scope_id):
        """Performs a GET call to retrieve Global Scope Map then finds matching scope.

        Args:
            central_conn (NewCentralBase): Established Central connection object
            scope_id (int): ID of the scope to be matched on

        Returns:
            (list): List of assigned profile dictionaries for the scope
        """
        assigned_profiles = []
        mappings = self.get(central_conn=central_conn)
        if mappings:
            for mapping in mappings:
                if mapping["scope-name"] == scope_id:
                    assigned_profiles.append(mapping)
        for profile in assigned_profiles:
            profile.pop("scope-name")
        return assigned_profiles

    def associate_profile_to_scope(
        self,
        central_conn,
        scope_id,
        profile_name,
        persona=None,  # remove persona in 2.x
        *,
        device_function=None,
    ):
        """Performs a POST call to associate a profile with device function to the provided scope.

        Args:
            central_conn (NewCentralBase): Established Central connection object
            scope_id (int or str): ID of the scope to associate the profile
            profile_name (str): Name of the profile to be assigned
            persona (str or list, optional): Deprecated alias of device_function.
            device_function (str or list): Device function(s) to be associated
                with the profile. One or more of ALL_DEVICE_FUNCTIONS, or "ALL".

        Returns:
            (dict): Response of the first failed POST call, or of the last
                call if all succeeded
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=persona
        )
        return self._scope_map_call(
            "POST", central_conn, scope_id, profile_name, device_function
        )

    def unassociate_profile_from_scope(
        self,
        central_conn,
        scope_id,
        profile_name,
        persona=None,  # remove persona in 2.x
        *,
        device_function=None,
    ):
        """Performs a DELETE call to unassign a profile with device function from the provided scope.

        Args:
            central_conn (NewCentralBase): Established Central connection object
            scope_id (int or str): ID of the scope to unassociate the profile from
            profile_name (str): Name of the profile to be unassigned
            persona (str or list, optional): Deprecated alias of device_function.
            device_function (str or list): Device function(s) to be unassociated
                from the profile. One or more of ALL_DEVICE_FUNCTIONS, or "ALL".

        Returns:
            (dict): Response of the first failed DELETE call, or of the last
                call if all succeeded
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=persona
        )
        return self._scope_map_call(
            "DELETE", central_conn, scope_id, profile_name, device_function
        )

    def _scope_map_call(
        self, api_method, central_conn, scope_id, profile_name, device_function
    ):
        """Sends one scope-maps call per valid device function.

        Returns:
            (dict): Response of the first failed call, or of the last call
        """
        if not profile_name:
            raise ParameterError("profile_name is required and cannot be empty")
        if not device_function:
            raise ParameterError("device_function is required and cannot be empty")
        if isinstance(device_function, str):
            device_function = (
                ALL_DEVICE_FUNCTIONS
                if device_function == "ALL"
                else [device_function]
            )
        action = "assign" if api_method == "POST" else "unassign"
        responses = []
        for df in device_function:
            if df not in ALL_DEVICE_FUNCTIONS:
                central_conn.logger.error(
                    f"{df} is not a valid device function. Unable to {action} profile {profile_name} for scope {scope_id}"
                )
                continue
            api_data = {
                "scope-map": [
                    {
                        "scope-name": str(scope_id),
                        "persona": df,
                        "resource": profile_name,
                    }
                ]
            }
            resp = central_conn.command(
                api_method=api_method,
                api_path=generate_url(SCOPE_URLS["SCOPE-MAPS"]),
                api_data=api_data,
            )
            if resp["code"] == 200:
                central_conn.logger.info(
                    f"Successfully {action}ed profile {profile_name} for {scope_id} with {df} device function"
                )
            responses.append(resp)
        if not responses:
            raise ParameterError(
                f"No valid device function provided. Valid values: {', '.join(ALL_DEVICE_FUNCTIONS)} or ALL"
            )
        return next((r for r in responses if r["code"] != 200), responses[-1])
