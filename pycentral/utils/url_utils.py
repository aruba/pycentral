# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

versions = ["v1alpha1", "v1", "v1alpha2"]

CATEGORIES = {
    "configuration": {
        "value": "network-config",
        "type": "configuration",
        "latest": "v1alpha1",
    },
    "monitoring": {
        "value": "network-monitoring",
        "type": "monitoring",
        "latest": "v1",
    },
    "troubleshooting": {
        "value": "network-troubleshooting",
        "type": "troubleshooting",
        "latest": "v1alpha1",
    },
    "subscriptions": {"value": "subscriptions", "type": "glp", "latest": "v1"},
    "user_management": {"value": "identity", "type": "glp", "latest": "v1"},
    "devices": {"value": "devices", "type": "glp", "latest": "v1"},
    "service_catalog": {
        "value": "service-catalog",
        "type": "glp",
        "latest": "v1",
    },
    "notifications": {
        "value": "network-notifications",
        "type": "monitoring",
        "latest": "v1",
    },
    "services": {
        "value": "network-services",
        "type": "monitoring",
        "latest": "v1",
    },
}


def get_prefix(category="configuration", version="latest"):
    """Generate URL prefix for a given category and version.

    Args:
        category (str, optional): API category name.
        version (str, optional): API version.

    Returns:
        (str): URL prefix in the format "category_value/version/".

    Raises:
        ValueError: If category is not supported or version is invalid.
    """
    if category not in CATEGORIES:
        raise ValueError(
            f"Invalid category: {category}, Supported categories: {list(CATEGORIES.keys())}"
        )
    category_value = CATEGORIES[category]["value"]
    if version == "latest":
        version = CATEGORIES[category]["latest"]
    else:
        if version not in versions:
            raise ValueError(
                f"Invalid version: {version}. Allowed versions: {versions}"
            )
    return f"{category_value}/{version}/"


def generate_url(api_endpoint, category="configuration", version="latest"):
    """Generate complete API URL for a given endpoint, category, and version.

    Args:
        api_endpoint (str): The API endpoint path to append to the URL.
        category (str, optional): API category name.
        version (str, optional): API version.

    Returns:
        (str): Complete API URL in the format "category[value]/version/api_endpoint".

    Raises:
        ValueError: If category is not supported or version is invalid.
        TypeError: If api_endpoint is not a string.
    """
    if category not in CATEGORIES:
        raise ValueError(
            f"Invalid category: {category}, Supported categories: {list(CATEGORIES.keys())}"
        )
    if api_endpoint is not None and not isinstance(api_endpoint, str):
        raise TypeError(
            f"Invalid type: {type(api_endpoint)} for api_endpoint, expected str"
        )
    category_value = CATEGORIES[category]["value"]
    if version == "latest":
        version = CATEGORIES[category]["latest"]
    else:
        if version not in versions:
            raise ValueError(
                f"Invalid version: {version}. Allowed versions: {versions}"
            )
    return f"{category_value}/{version}/{api_endpoint}"
