# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils import SCOPE_URLS, generate_url
from ..utils.scope_utils import (
    set_attributes,
    get_scope_element,
    rename_keys,
)
from .site import Site
from ..exceptions import ParameterError
from .scope_base import ScopeBase

OPTIONAL_ATTRIBUTES = {
    "id": None,
    "associated_sites": 0,
    "associated_devices": 0,
}

OBJECT_ATTRIBUTES = {"assigned_profiles": [], "sites": []}

API_ATTRIBUTE_MAPPING = {
    "id": "id",
    "scopeName": "name",
    "description": "description",
    "siteCount": "associated_sites",
    "deviceCount": "associated_devices",
}

REQUIRED_ATTRIBUTES = ["name", "description"]


class Site_Collection(ScopeBase):
    """This class holds site collection and all of its attributes & related methods."""

    def __init__(
        self, collection_attributes, central_conn=None, from_api=False
    ):
        """Constructor for Site Collection object.

        Args:
            collection_attributes (dict): Attributes of the site collection
            central_conn (NewCentralBase, optional): Instance of NewCentralBase to establish
                connection to Central.
            from_api (bool, optional): Boolean indicates if the collection_attributes is from
                the Central API response.

        Raises:
            ValueError: If unexpected or missing attributes are provided
        """
        if from_api:
            collection_attributes = rename_keys(
                collection_attributes, API_ATTRIBUTE_MAPPING
            )
        else:
            valid_attributes = REQUIRED_ATTRIBUTES + ["sites"]
            for attribute in collection_attributes:
                if attribute not in valid_attributes:
                    raise ValueError(
                        f"Unexpected attribute: {attribute}. For collection_attributes(not via API) only the following attributes are supported - {', '.join(valid_attributes)}"
                    )
        self.materialized = from_api
        self.central_conn = central_conn
        self.type = "site_collection"
        self.id = None

        missing_required_attributes = [
            attr
            for attr in REQUIRED_ATTRIBUTES
            if attr not in collection_attributes
        ]
        if missing_required_attributes:
            raise ValueError(
                f"Missing required attributes: {', '.join(missing_required_attributes)}"
            )

        valid_attributes = (
            REQUIRED_ATTRIBUTES
            + list(OPTIONAL_ATTRIBUTES.keys())
            + list(OBJECT_ATTRIBUTES.keys())
        )
        unexpected_attributes = [
            attr
            for attr in collection_attributes
            if attr not in valid_attributes
        ]
        if unexpected_attributes:
            raise ValueError(
                f"Unexpected attributes: {', '.join(unexpected_attributes)}.\n If site_collections is being created based off api_response ensure that the from_api flag is set to True"
            )
        set_attributes(
            obj=self,
            attributes_dict=collection_attributes,
            required_attributes=REQUIRED_ATTRIBUTES,
            optional_attributes=OPTIONAL_ATTRIBUTES,
            object_attributes=OBJECT_ATTRIBUTES,
        )

    def create(self):
        """Perform a POST call to create a site collection on Central.

        Returns:
            (bool): True if site collection was created, False otherwise

        Raises:
            Exception: If site collection already exists or central connection is missing
        """
        if self.materialized:
            raise Exception(
                "Unable to create a site collection that already exists"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_collection_creation_status = False
        api_method = "POST"
        api_path = generate_url(SCOPE_URLS["SITE_COLLECTION"])
        api_data = self.__generate_api_body()

        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200:
            try:
                site_collection_id = resp["msg"]["items"][0]
                self.id = int(site_collection_id)
                self.materialized = True
                site_collection_creation_status = True
                self.get()
                self.central_conn.logger.info(
                    f"Successfully created site collection {self.get_name()} in Central"
                )
            except KeyError:
                self.central_conn.logger.info(
                    f"Failed to set site collection id of site collection {self.get_name()}"
                )
                pass
        else:
            self.central_conn.logger.error(
                f"Failed to create site collection {self.get_name()} in Central.\nError message - {resp['msg']}"
            )
        return site_collection_creation_status

    def get(self):
        """Performs a GET call to retrieve data of a site collection then sets attributes.

        Returns:
            (dict): JSON Data of GET call if success, None otherwise

        Raises:
            Exception: If site collection doesn't exist or central connection is missing
        """
        if not self.materialized:
            raise Exception(
                "Unable to get a site collection that does not exist"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_collection_data = get_scope_element(
            obj=self, scope="site_collection", scope_id=self.get_id()
        )

        if not site_collection_data:
            self.materialized = False
            self.central_conn.logger.error(
                f"Unable to fetch site collection {self.get_name()} from Central"
            )
        else:
            collection_attributes = rename_keys(
                site_collection_data, API_ATTRIBUTE_MAPPING
            )
            set_attributes(
                obj=self,
                attributes_dict=collection_attributes,
                required_attributes=REQUIRED_ATTRIBUTES,
                optional_attributes=OPTIONAL_ATTRIBUTES,
            )
            self.central_conn.logger.info(
                f"Successfully fetched site collection {self.get_name()} from Central."
            )
        return site_collection_data

    def update(self):
        """Performs a PUT call to update attributes of site collection on Central if changes are detected.

        The source of truth is self.

        Returns:
            (bool): True if modifications were made, False otherwise

        Raises:
            Exception: If site collection doesn't exist on Central or central connection is missing
        """
        if not self.materialized:
            raise Exception(
                "Unable to update a site collection that does not exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        modified = False
        site_collection_data = get_scope_element(
            obj=self, scope="site_collection", scope_id=self.get_id()
        )

        if not site_collection_data:
            self.materialized = False
            raise Exception(
                "Unable to upate site collection as it could not be found in Central."
            )

        collection_attributes = rename_keys(
            site_collection_data, API_ATTRIBUTE_MAPPING
        )

        object_attributes = {
            key: getattr(self, key) for key in API_ATTRIBUTE_MAPPING.values()
        }

        if collection_attributes != object_attributes:
            api_method = "PUT"
            api_path = generate_url(SCOPE_URLS["SITE_COLLECTION"])
            api_data = self.__generate_api_body()

            resp = self.central_conn.command(
                api_method=api_method, api_path=api_path, api_data=api_data
            )
            if resp["code"] == 200:
                modified = True
                self.central_conn.logger.info(
                    f"Successfully updated site collection {self.get_name()} in Central"
                )
            else:
                self.central_conn.logger.info(
                    f"Failed to update site collection {self.get_name()} in Central.\n Error message - {resp['msg']}"
                )
        return modified

    def delete(self):
        """Performs DELETE call to delete Site Collection.

        Returns:
            (bool): True if DELETE was successful, False otherwise

        Raises:
            Exception: If site collection doesn't exist on Central or central connection is missing
        """
        if not self.materialized:
            raise Exception(
                "Unable to delete a site collection that doesn't exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_collection_deletion_status = False
        api_method = "DELETE"
        api_path = generate_url(SCOPE_URLS["SITE_COLLECTION_BULK"])
        api_data = {"items": [{"id": str(self.get_id())}]}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200:
            self.id = None
            self.materialized = False
            site_collection_deletion_status = True
            self.central_conn.logger.info(
                f"Successfully deleted site collection {self.get_name()}"
            )
        else:
            self.central_conn.logger.error(
                f"Failed to delete site collection {self.get_name()} (remove its sites first if any remain).\n Error message - {resp['msg']}"
            )
        return site_collection_deletion_status

    def associate_site(self, sites):
        """Performs POST call to associate sites with a site collection.

        Args:
            sites (list): List of Site objects or list of site IDs (int) to associate
                with this site collection

        Returns:
            (bool): True if site association was successful, False otherwise

        Raises:
            ParameterError: If sites parameter is not a list of Site or int types
        """
        api_method = "POST"
        api_path = generate_url(SCOPE_URLS["ADD_SITE_TO_COLLECTION"])

        if all(isinstance(site, Site) for site in sites):
            site_ids = [str(site.get_id()) for site in sites]
        elif all(isinstance(site_id, int) for site_id in sites):
            site_ids = [str(site_id) for site_id in sites]
        else:
            raise ParameterError(
                "sites parameter should only be a list of type Site or int"
            )

        api_data = {
            "siteCollectionId": str(self.get_id()),
            "siteIds": site_ids,
        }
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200 and len(resp["msg"]["items"]) == len(site_ids):
            self.central_conn.logger.info(
                f"Successfully associated site(s) {', '.join(str(getattr(site, 'name', site)) for site in sites)} to site collection {self.name}"
            )
            self.get()
            for site in sites:
                if isinstance(site, Site):
                    self.add_site(site_id=site.get_id())
                    site.add_site_collection(
                        site_collection_id=self.get_id(),
                        site_collection_name=self.get_name(),
                    )
                elif isinstance(site, int):
                    self.add_site(site_id=site)
            return True
        else:
            self.central_conn.logger.error(
                f"Failed to associate site(s) {', '.join(str(getattr(site, 'name', site)) for site in sites)} to site collection {self.name}.\n Error message - {resp['msg']}"
            )
            return False

    def unassociate_site(self, sites):
        """Performs DELETE call to unassociate sites with a site collection.

        Args:
            sites (list): List of Site objects or list of site IDs (int) to unassociate
                from this site collection

        Returns:
            (bool): True if site unassociation was successful, False otherwise

        Raises:
            ParameterError: If sites parameter is not a list of Site or int types
        """
        api_method = "DELETE"
        api_path = generate_url(SCOPE_URLS["REMOVE_SITE_FROM_COLLECTION"])
        if all(isinstance(site, Site) for site in sites):
            site_ids = [str(site.get_id()) for site in sites]
        elif all(isinstance(site_id, int) for site_id in sites):
            site_ids = [str(site_id) for site_id in sites]
        else:
            raise ParameterError(
                "sites parameter should only be a list of type Site or int"
            )
        api_params = {"site-id": ",".join(site_ids)}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_params=api_params
        )
        if resp["code"] == 200 and len(resp["msg"]["items"]) == len(site_ids):
            self.central_conn.logger.info(
                f"Successfully unassociated site(s) {', '.join(str(getattr(site, 'name', site)) for site in sites)} from site collection {self.name}"
            )
            self.get()
            for site in sites:
                if isinstance(site, Site):
                    site.remove_site_collection()
                    self.remove_site(site_id=site.get_id())
                elif isinstance(site, int):
                    self.remove_site(site_id=site)
            return True
        else:
            self.central_conn.logger.error(
                f"Failed to unassociate site(s) {', '.join(str(getattr(site, 'name', site)) for site in sites)} to site collection {self.name}.\n Error message - {resp['msg']}"
            )
            return False

    def add_site(self, site_id):
        """Adds the site details (site ID) to the site collection attributes.

        Args:
            site_id (int or str): Site ID of the site

        Returns:
            (bool): True if site details were successfully updated, False otherwise
        """
        if int(site_id):
            self.sites.append(int(site_id))
            return True
        return False

    def remove_site(self, site_id):
        """Removes the site details (site ID) from the site collection attributes.

        Args:
            site_id (int): Site ID of the site

        Returns:
            (bool): True if site details were removed, False otherwise
        """
        if site_id in self.sites:
            self.sites.remove(site_id)
            return True
        return False

    def __str__(self):
        """Returns the string containing the name and ID of the site collection.

        Returns:
            (str): String representation of this class
        """
        return f"Site Collection ID - {self.get_id()}, Site Collection Name - {self.get_name()}"

    def __generate_api_body(self):
        """Returns the dictionary of site collection attributes needed for making API calls.

        Returns:
            (dict): Dictionary of site collection attributes needed for making API calls to Central
        """
        api_body = {
            "scopeName": self.name,
            "description": self.description,
        }
        if self.materialized:
            api_body["scopeId"] = str(self.get_id())
        elif len(self.sites) > 0:
            api_body["siteIds"] = [str(site_id) for site_id in self.sites]

        return api_body
