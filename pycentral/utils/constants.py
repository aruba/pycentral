# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

"""Constants used across the pycentral package.

This module contains constant values for API endpoints, cluster URLs,
and configuration mappings used throughout the pycentral SDK.

Attributes:
    CLUSTER_BASE_URLS (dict[str, str]): Public Central cluster
        names with their corresponding API Base URLs. You can update this
        dictionary to add your own private cluster details. You can learn more about Base URLs <a href="https://developer.arubanetworks.com/new-central/docs/getting-started-with-rest-apis#api-gateway-base-urls" target="_blank">here</a>.

    SUPPORTED_CONFIG_PERSONAS (dict[str, str]): Supported New Central Device Personas
        and their corresponding API values. You can learn more about Device Personas <a href="https://developer.arubanetworks.com/new-central/docs/device-function-and-persona" target="_blank">here</a>.

    AUTHENTICATION (dict[str, str]): Authentication endpoints for OAuth flows for token creation.

    GLP_URLS (dict[str, str]): GreenLake Platform (GLP) API URLs and endpoints.

    SCOPE_URLS (dict[str, str]): Scope-related API URLs for site and device
        organization.
"""

CLUSTER_BASE_URLS = {
    "EU-1": "https://de1.api.central.arubanetworks.com",
    "EU-Central2": "https://de2.api.central.arubanetworks.com",
    "EU-Central3": "https://de3.api.central.arubanetworks.com",
    "UK": "https://gb1.api.central.arubanetworks.com",
    "US-1": "https://us1.api.central.arubanetworks.com",
    "US-2": "https://us2.api.central.arubanetworks.com",
    "US-WEST-4": "https://us4.api.central.arubanetworks.com",
    "US-WEST-5": "https://us5.api.central.arubanetworks.com",
    "US-East1": "https://us6.api.central.arubanetworks.com",
    "Canada-1": "https://ca1.api.central.arubanetworks.com",
    "APAC-1": "https://in1.api.central.arubanetworks.com",
    "APAC-EAST1": "https://jp1.api.central.arubanetworks.com",
    "APAC-SOUTH1": "https://au1.api.central.arubanetworks.com",
    "UAE": "https://ae1.api.central.arubanetworks.com",
    "China": "https://cn1.api.central.arubanetworks.com.cn",
    "Internal": "https://internal.api.central.arubanetworks.com",
}

SUPPORTED_CONFIG_PERSONAS = {
    "Campus AP": "CAMPUS_AP",
    "Micro Branch AP": "MICROBRANCH_AP",
    "Access Switch": "ACCESS_SWITCH",
    "Core Switch": "CORE_SWITCH",
    "Aggregation Switch": "AGG_SWITCH",
    "Mobility Gateway": "MOBILITY_GW",
    "Branch GW": "BRANCH_GW",
    "Bridge": "BRIDGE",
    "Hybrid NAC": "HYBRID_NAC",
}

AUTHENTICATION = {
    "OAUTH": "https://sso.common.cloud.hpe.com/as/token.oauth2",
    # This is te token issuer URL used for unified credential management
    "OAUTH_GLOBAL": "https://global.api.greenlake.hpe.com/authorization/v2/oauth2",
}
GLP_URLS = {
    "BaseURL": "https://global.api.greenlake.hpe.com",
    "DEVICE": "devices",
    "SUBSCRIPTION": "subscriptions",
    "USER_MANAGEMENT": "users",
    "ASYNC": "async-operations",
    "SERVICE_MANAGER": "service-managers",
    "SERVICE_MANAGER_PROVISIONS": "service-manager-provisions",
    "SERVICE_MANAGER_BY_REGION": "per-region-service-managers",
}

SCOPE_URLS = {
    "SITE": "sites",
    "SITE_COLLECTION": "site-collections",
    "DEVICE": "devices",
    "DEVICE_GROUP": "device-collections",
    "ADD_SITE_TO_COLLECTION": "site-collection-add-sites",
    "REMOVE_SITE_FROM_COLLECTION": "site-collection-remove-sites",
    "HIERARCHY": "hierarchy",
    "SCOPE-MAPS": "scope-maps",
}

VALID_PERSONAS = [
    "SERVICE_PERSONA",
    "HYBRID_NAC",
    "CORE_SWITCH",
    "BRIDGE",
    "CAMPUS_AP",
    "IOT",
    "MOBILITY_GW",
    "AGG_SWITCH",
    "BRANCH_GW",
    "VPNC",
    "ACCESS_SWITCH",
    "MICROBRANCH_AP",
]

__all__ = [
    "CLUSTER_BASE_URLS",
    "SUPPORTED_CONFIG_PERSONAS",
    "AUTHENTICATION",
    "GLP_URLS",
    "SCOPE_URLS",
    "VALID_PERSONAS",
]
