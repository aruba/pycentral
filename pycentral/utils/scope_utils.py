# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.utils import SCOPE_URLS, generate_url
import copy
import pycountry

SUPPORTED_SCOPES = ["site", "site_collection", "device", "device_group"]
# Scopes that have a network-config list endpoint
LISTABLE_SCOPES = ["site", "site_collection", "device_group"]
DEFAULT_LIMIT = 100
# API keys whose values are converted to int when renamed
INTEGER_KEYS = {"id", "scopeId", "collectionId", "deviceCount", "siteCount"}


def fetch_attribute(obj, attribute):
    """Fetch the value associated with the provided attribute in the object.

    Args:
        obj (object): Object whose attribute has to be returned.
        attribute (str): Attribute within the object that has to be returned.

    Returns:
        (any): Value of the required attribute if it exists, None otherwise.
    """
    if hasattr(obj, attribute):
        return getattr(obj, attribute)
    return None


def update_attribute(obj, attribute, new_value):
    """Update the value of the provided attribute in the object.

    Args:
        obj (object): Object whose attribute has to be updated.
        attribute (str): Attribute within the object that has to be updated.
        new_value (any): New value to set for the attribute.

    Returns:
        (bool): True if the attribute was successfully updated, False otherwise.
    """
    if hasattr(obj, attribute):
        setattr(obj, attribute, new_value)
        return True
    return False


def is_supported_scope(obj, scope, supported=SUPPORTED_SCOPES):
    """Check the scope is supported, logging an error if it is not.

    Args:
        obj (object): Class instance with a central_conn used for logging.
        scope (str): The type of the element.
        supported (list, optional): Supported scope types.

    Returns:
        (bool): True if the scope is supported, False otherwise.
    """
    if scope in supported:
        return True
    obj.central_conn.logger.error(
        f"Unknown scope '{scope}'. Please provide one of the supported scopes - {', '.join(supported)}"
    )
    return False


def get_all_scope_elements(obj, scope):
    """Make GET API calls to Central to get all elements of the specified scope.

    This method is supported for site, site collection, and device groups scopes.

    Args:
        obj (object): Class instance that will be used to make API calls to Central.
        scope (str): The type of the element. Valid values: "site", "site_collection",
            "device_group".

    Returns:
        (list or None): List of all scope elements, or None if there are errors.
    """
    if not is_supported_scope(obj, scope, LISTABLE_SCOPES):
        return None
    limit = DEFAULT_LIMIT
    offset = 0
    scope_elements = []
    number_of_scope_elements = None
    while (
        number_of_scope_elements is None
        or len(scope_elements) < number_of_scope_elements
    ):
        resp = get_scope_elements(obj, scope, limit=limit, offset=offset)
        if resp["code"] == 200:
            offset += limit
            resp_message = resp["msg"]
            if number_of_scope_elements is None:
                number_of_scope_elements = resp_message["total"]

            scope_elements.extend(
                [scope_element for scope_element in resp_message["items"]]
            )
        else:
            obj.central_conn.logger.error(resp["msg"])
            break
    obj.central_conn.logger.info(
        f"Total {scope}s fetched from account: {len(scope_elements)}"
    )
    return scope_elements


def get_scope_elements(
    obj, scope, limit=50, offset=0, filter_field="", sort=""
):
    """Make GET API calls to Central to get scope elements based on provided attributes.

    This method is supported for site, site collection, and device groups scopes.

    Args:
        obj (object): Class instance that will be used to make API calls to Central.
        scope (str): The type of the element. Valid values: "site", "site_collection",
            "device_group".
        limit (int, optional): Number of scope elements to be fetched.
        offset (int, optional): Pagination start index.
        filter_field (str, optional): Field for sorting. For sites: scopeName, address,
            state, country, city, deviceCount, collectionName, zipcode, timezone.
            For site_collection: scopeName, description, deviceCount, siteCount.
        sort (str, optional): Direction of sorting. Accepted values: ASC or DESC.

    Returns:
        (dict or None): API response with scope elements, or None if there are errors.
    """
    if not is_supported_scope(obj, scope, LISTABLE_SCOPES):
        return None

    api_path = generate_url(SCOPE_URLS[scope.upper()])
    api_method = "GET"
    api_params = {"limit": limit, "offset": offset}

    if filter_field:
        api_params["filter"] = filter_field
    if sort:
        api_params["sort"] = sort

    resp = obj.central_conn.command(
        api_method=api_method, api_path=api_path, api_params=api_params
    )
    return resp


def set_attributes(
    obj,
    attributes_dict,
    required_attributes,
    optional_attributes=None,
    object_attributes=None,
):
    """Set attributes of the given object based on the attributes dictionary.

    Args:
        obj (object): Class instance whose attributes will be set.
        attributes_dict (dict): Dictionary of attributes to set on the object.
        required_attributes (list): List of required attribute names.
        optional_attributes (dict, optional): Dictionary of optional attributes with
            their default values.
        object_attributes (dict, optional): Dictionary of object-type attributes with
            their default values.
    """
    for attr in required_attributes:
        value = attributes_dict[attr]
        setattr(obj, attr, value)

    if optional_attributes:
        for attr, default_value in optional_attributes.items():
            value = attributes_dict.get(attr)
            if not value:
                value = copy.deepcopy(default_value)
            setattr(obj, attr, value)
    if object_attributes:
        for attr, default_value in object_attributes.items():
            setattr(
                obj,
                attr,
                attributes_dict.get(attr, copy.deepcopy(default_value)),
            )


def get_scope_element(obj, scope, scope_id=None):
    """Make GET API calls to Central to find the specified scope element.

    This method is supported for site, site collection, and device groups scopes.

    Args:
        obj (object): Class instance that will be used to make API calls to Central.
        scope (str): The type of the element. Valid values: "site", "site_collection",
            "device_group".
        scope_id (int, optional): ID of the scope element to be returned.

    Returns:
        (dict or None): Attributes of the scope element if found, None otherwise.
    """
    if not is_supported_scope(obj, scope, LISTABLE_SCOPES):
        return None
    if scope_id is None:
        obj.central_conn.logger.error("Scope ID must be provided.")
        return None

    scope_elements_list = get_all_scope_elements(obj=obj, scope=scope)
    if not scope_elements_list:
        return None

    for element in scope_elements_list:
        if element.get("scopeId") == str(scope_id):
            return element

    return None


def rename_keys(api_dict, api_attribute_mapping):
    """Rename the keys of attributes from the API response.

    Keys missing from api_attribute_mapping are skipped, so new fields added
    by the API do not break object creation. Id/count keys are converted to
    int, a timezone dict to its timezoneId and isProvisioned to a bool.

    Args:
        api_dict (dict): Dictionary of information from Central API Response.
        api_attribute_mapping (dict): Dictionary mapping API keys to object attributes.

    Returns:
        (dict): Renamed dictionary with keys mapped to object attributes.
    """
    renamed_dict = {}
    for key, value in api_dict.items():
        new_key = api_attribute_mapping.get(key)
        if new_key is None:
            continue
        if key in INTEGER_KEYS and value not in (None, ""):
            value = int(value)
        elif key == "timezone" and isinstance(value, dict):
            value = value.get("timezoneId")
        elif key == "isProvisioned":
            value = value == "Yes"
        renamed_dict[new_key] = copy.deepcopy(value)
    return renamed_dict


def validate_find_scope_elements(ids=None, names=None, serials=None, scope=""):
    """Validate the input parameters for finding scope elements.

    Args:
        ids (str or list, optional): ID(s) of the element(s).
        names (str or list, optional): Name(s) of the element(s).
        serials (str or list, optional): Serial number(s) of the element(s) (only for devices).
        scope (str, optional): Specific scope to search in (e.g., "site", "device").

    Raises:
        ValueError: If validation fails due to multiple parameters or invalid scope for serials.
    """
    # Ensure only one of ids, names, or serials is provided
    provided_params = [ids, names, serials]
    if sum(param is not None for param in provided_params) > 1:
        raise ValueError("Provide only one of 'ids', 'names', or 'serials'.")

    # If serials are provided, ensure the scope is "device" or no scope is provided
    if serials and scope and scope.lower() != "device":
        raise ValueError(
            "Serials can only be used with the 'device' scope or when no scope is provided."
        )


def validate_iso_location(state=None, country=None, city=None):
    """Validate the input parameters for ISO 3166-1 short name format for location.

    Args:
        state (str, optional): State name, i.e., "California".
        country (str, optional): Country name, i.e., "United States".
        city (str, optional): City name, i.e., "San Francisco".

    Raises:
        ValueError: If validation fails invalid values.
    """
    # Ensure that at least one of state, country, or city is provided and they're all strings if provided
    if not any([state, country, city]) or not all(
        isinstance(param, str)
        for param in [state, country, city]
        if param is not None
    ):
        raise ValueError(
            "At least one of 'state', 'country', or 'city' must be provided and all must be strings if provided"
        )

    # Validate Country using pycountry
    if country:
        try:
            pycountry.countries.lookup(country)
        except LookupError:
            raise ValueError(
                f"Invalid country name: {country} Must be in ISO 3166 short name format, e.g., 'United States'"
            )
    # Validate State using pycountry
    if state:
        try:
            pycountry.subdivisions.lookup(state)
        except LookupError:
            raise ValueError(
                f"Invalid state name: {state} Must be in ISO 3166 short name format, e.g., 'California'"
            )

    # Validate City as a non-empty string if provided
    if city is not None and not city.strip():
        raise ValueError("City name must be a non-empty string.")


def lookup_in_map(keys, lookup_map):
    """Perform lookup in a map for the given key(s).

    Args:
        keys (str, int, or list): Key(s) to look up.
        lookup_map (dict): Map to search in.

    Returns:
        (any or list or None): Found value(s) or None if not found.
    """
    if isinstance(keys, (str, int)):
        return lookup_map.get(keys)
    return [lookup_map.get(key) for key in keys if key in lookup_map]
