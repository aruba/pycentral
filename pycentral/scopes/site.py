# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_base import ScopeBase
from ..utils import SCOPE_URLS, generate_url
import pytz
from datetime import datetime
from ..utils.scope_utils import (
    fetch_attribute,
    update_attribute,
    set_attributes,
    get_scope_element,
    rename_keys,
    validate_iso_location,
)

API_ATTRIBUTE_MAPPING = {
    "id": "id",
    "scopeName": "name",
    "address": "address",
    "city": "city",
    "state": "state",
    "country": "country",
    "zipcode": "zipcode",
    "longitude": "longitude",
    "latitude": "latitude",
    "collectionName": "site_collection_name",
    "collectionId": "site_collection_id",
    "deviceCount": "associated_devices",
    "timezone": "timezone",
    "image": "image",
}

REQUIRED_ATTRIBUTES = [
    "name",
    "address",
    "city",
    "state",
    "country",
    "zipcode",
    "timezone",
]

OPTIONAL_ATTRIBUTES = {
    "id": None,
    "latitude": None,
    "longitude": None,
    "image": {"name": "", "contentType": ""},
    "associated_devices": 0,
    "devices": [],
    "site_collection_name": None,
    "site_collection_id": None,
    "assigned_profiles": [],
}


class Site(ScopeBase):
    """This class holds site and all of its attributes & related methods."""

    def __init__(self, site_attributes, central_conn=None, from_api=False):
        """Constructor for Site object.

        Args:
            site_attributes (dict): Attributes of the site collection
            central_conn (NewCentralBase, optional): Instance of NewCentralBase to establish
                connection to Central.
            from_api (bool, optional): Boolean indicates if the site_attributes is from
                the Central API response.

        Raises:
            ValueError: If unexpected or missing attributes are provided
        """
        if from_api:
            site_attributes = rename_keys(
                site_attributes, API_ATTRIBUTE_MAPPING
            )

        self.materialized = from_api
        self.central_conn = central_conn
        self.id = None
        self.type = "site"

        missing_required_attributes = [
            attr for attr in REQUIRED_ATTRIBUTES if attr not in site_attributes
        ]
        if missing_required_attributes:
            raise ValueError(
                f"Missing required attributes: {', '.join(missing_required_attributes)}"
            )
        valid_attributes = REQUIRED_ATTRIBUTES + list(
            OPTIONAL_ATTRIBUTES.keys()
        )
        unexpected_attributes = [
            attr for attr in site_attributes if attr not in valid_attributes
        ]
        if unexpected_attributes:
            raise ValueError(
                f"Unexpected attributes: {', '.join(unexpected_attributes)}.\n If site is being created based off api_response ensure that the from_api flag is set to True"
            )
        set_attributes(
            obj=self,
            attributes_dict=site_attributes,
            required_attributes=REQUIRED_ATTRIBUTES,
            optional_attributes=OPTIONAL_ATTRIBUTES,
        )

    def create(self):
        """Perform a POST call to create a site on Central.

        The v1 API requires latitude and longitude; set them in
        site_attributes (no geocoding is done by the SDK).

        Returns:
            (bool): True if site was created, False otherwise

        Raises:
            Exception: If site already exists or central connection is missing
        """
        if self.materialized:
            raise Exception("Unable to create a site that already exists")

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_creation_status = False
        api_method = "POST"
        api_path = generate_url(SCOPE_URLS["SITE"])
        api_data = self.__generate_api_body()

        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200:
            try:
                site_id = resp["msg"]["items"][0]
                self.id = int(site_id)
                self.materialized = True
                site_creation_status = True
                self.get()
                self.central_conn.logger.info(
                    f"Successfully created site {self.get_name()} in Central"
                )
            except KeyError:
                self.central_conn.logger.info(
                    f"Failed to set site id of site {self.get_name()}"
                )
                pass
        else:
            self.central_conn.logger.error(
                f"Failed to create site {self.get_name()} in Central.\nError message - {resp['msg']}"
            )
        return site_creation_status

    def get(self):
        """Performs a GET call to retrieve data of a site then sets attributes of self.

        Returns:
            (dict): JSON Data of GET call if success, None otherwise

        Raises:
            Exception: If site doesn't exist or central connection is missing
        """
        if not self.materialized:
            raise Exception("Unable to get a site that does not exist")

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_data = get_scope_element(
            obj=self, scope="site", scope_id=self.get_id()
        )
        if not site_data:
            self.materialized = False
            self.central_conn.logger.error(
                f"Unable to fetch site {self.get_name()} from Central"
            )
        else:
            site_attributes = rename_keys(site_data, API_ATTRIBUTE_MAPPING)
            set_attributes(
                obj=self,
                attributes_dict=site_attributes,
                required_attributes=REQUIRED_ATTRIBUTES,
                optional_attributes=OPTIONAL_ATTRIBUTES,
            )
            self.central_conn.logger.info(
                f"Successfully fetched site {self.get_name()} from Central."
            )
        return site_data

    def update(self):
        """Performs a PUT call to update attributes of site on Central if changes are detected.

        The source of truth is self.

        Returns:
            (bool): True if modifications were made, False otherwise

        Raises:
            Exception: If site doesn't exist on Central or central connection is missing
        """
        if not self.materialized:
            raise Exception(
                "Unable to update a site that does not exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        modified = False
        site_data = get_scope_element(
            obj=self, scope="site", scope_id=self.get_id()
        )

        if not site_data:
            self.materialized = False
            raise Exception(
                "Unable to upate site as it could not be found in Central."
            )

        site_attributes = rename_keys(site_data, API_ATTRIBUTE_MAPPING)

        object_attributes = {
            key: getattr(self, key) for key in API_ATTRIBUTE_MAPPING.values()
        }

        if site_attributes != object_attributes:
            api_method = "PUT"
            api_path = generate_url(SCOPE_URLS["SITE"])
            api_data = self.__generate_api_body()

            resp = self.central_conn.command(
                api_method=api_method, api_path=api_path, api_data=api_data
            )
            if resp["code"] == 200:
                modified = True
                self.central_conn.logger.info(
                    f"Successfully updated site {self.get_name()} in Central"
                )
            else:
                self.central_conn.logger.info(
                    f"Failed to update site {self.get_name()} in Central.\n Error message - {resp['msg']}"
                )
        return modified

    def delete(self):
        """Performs DELETE call to delete Site.

        Returns:
            (bool): True if DELETE was successful, False otherwise

        Raises:
            Exception: If site doesn't exist on Central or central connection is missing
        """
        if not self.materialized:
            raise Exception(
                "Unable to delete a site that doesn't exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_deletion_status = False
        api_method = "DELETE"
        api_path = generate_url(SCOPE_URLS["SITE_BULK"])
        api_data = {"items": [{"id": str(self.get_id())}]}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200:
            self.id = None
            self.materialized = False
            site_deletion_status = True
            self.central_conn.logger.info(
                f"Successfully deleted site {self.get_name()}"
            )

        else:
            self.central_conn.logger.error(
                f"Failed to delete site {self.get_name()}.\n Error message - {resp['msg']}"
            )
        return site_deletion_status

    def get_site_collection_attributes(self):
        """Returns dictionary of site collection attributes of the site.

        Returns:
            (dict or None): Dictionary of site collection attributes with 'id' and 'name' keys,
                or None if site collection id is not defined
        """
        if fetch_attribute(self, "site_collection_id"):
            return {
                "id": fetch_attribute(self, "site_collection_id"),
                "name": fetch_attribute(self, "site_collection_name"),
            }
        return None

    def add_site_collection(self, site_collection_id, site_collection_name):
        """Sets the attributes site collection id and name of this site object.

        Args:
            site_collection_id (int or str): Site collection id
            site_collection_name (str): Site collection name
        """
        update_attribute(
            self, attribute="site_collection_id", new_value=site_collection_id
        )

        update_attribute(
            self,
            attribute="site_collection_name",
            new_value=site_collection_name,
        )

    def remove_site_collection(self):
        """Sets the attributes of site collection id and name to None."""

        update_attribute(self, attribute="site_collection_id", new_value=None)
        update_attribute(self, attribute="site_collection_name", new_value=None)

    def __str__(self):
        """Returns string containing the Site id and name.

        Returns:
            (str): String representation of this class
        """
        return f"Site ID - {self.get_id()}, Site Name - {self.get_name()}"

    def __generate_api_body(self):
        """Returns the dictionary of site attributes needed for making API calls.

        Returns:
            (dict): Dictionary of site attributes needed for making API calls to Central
        """
        # Validate location attributes follow ISO 3166 before building API body
        validate_iso_location(
            country=self.country, state=self.state, city=self.city
        )

        api_body = {
            "name": self.get_name(),
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zipcode": self.zipcode,
            "timezone": self.__get_timezone_attributes(),
        }
        # latitude/longitude are required by the v1 API; sent when set
        for key in ("latitude", "longitude"):
            if getattr(self, key, None) is not None:
                api_body[key] = getattr(self, key)
        if self.materialized:
            api_body["scopeId"] = str(self.get_id())

        return api_body

    def __get_timezone_attributes(self):
        """Returns the dictionary of timezone attributes needed for making API calls.

        Returns:
            (dict): Dictionary of timezone attributes with 'rawOffset', 'timezoneId',
                and 'timezoneName' keys needed for site management API calls to Central
        """
        timezone = pytz.timezone(self.timezone)
        current_time = datetime.now(timezone)
        raw_offset = int(current_time.utcoffset().total_seconds() * 1_000)

        return {
            "rawOffset": raw_offset,
            "timezoneId": self.timezone,
            "timezoneName": current_time.tzname(),
        }
