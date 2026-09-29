# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_base import ScopeBase
from ..utils.scope_utils import (
    get_scope_elements,
    get_all_scope_elements,
    DEFAULT_LIMIT,
    SUPPORTED_SCOPES,
    is_supported_scope,
    validate_find_scope_elements,
    lookup_in_map,
)
from .device import Device
from .site import Site
from .site_collection import Site_Collection
from .scope_maps import get_config_assignments, get_scope_maps
from .device_group import Device_Group
from ..utils import SCOPE_URLS, generate_url
from ..utils.profile_utils import _resolve_device_function, _warn_deprecated
from ..exceptions import ParameterError
from concurrent.futures import ThreadPoolExecutor, as_completed


class Scopes(ScopeBase):
    """This class holds the Scopes (Global hierarchy) class & methods for managing sites & site collections."""

    def __init__(self, central_conn):
        """Constructor for Scopes object.

        Args:
            central_conn (NewCentralBase): Instance of NewCentralBase to establish connection to Central.

        Raises:
            ParameterError: If central_conn is None
        """
        if central_conn is None:
            raise ParameterError(
                "Central connection is required to create Scopes object."
            )
        self.central_conn = central_conn
        self.id = None
        self.name = "Global"
        self.type = "global"
        self.materialized = True
        self.assigned_profiles = []
        self._lookup_maps = {"id": {}, "serial": {}, "name": {}}

        self.site_collections = []
        self.sites = []
        self.devices = []
        self.device_groups = []

        self.get()

    def get(self):
        """Performs GET calls to Central to retrieve latest data of all scope elements.

        Fetches Global, Site Collections, Sites, Devices, & Device Groups from Central.

        Returns:
            (bool): True if all scope elements are successfully fetched, False otherwise
        """
        try:
            self.central_conn.logger.info(
                "Fetching all scopes (Global, Site Collection, Site, Device, Device Groups)..."
            )
            self.get_all_sites()
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        self.get_all_site_collections
                    ): "site_collections",
                    executor.submit(self.get_all_devices): "devices",
                    executor.submit(
                        self.get_all_device_groups
                    ): "device_groups",
                }

            for future in as_completed(futures):
                try:
                    future.result()  # Ensure exceptions are raised if any
                except Exception as e:
                    self.central_conn.logger.error(
                        f"Error fetching {futures[future]}: {e}"
                    )

            self.get_id()
            self._correlate_scopes()
            self.central_conn.logger.info(
                "Mapping configuration profiles to scopes..."
            )
            self.get_scope_profiles()

            self.central_conn.logger.info(
                "Successfully fetched configuration hierarchy details from Central"
            )
            self.materialized = True
            return True

        except Exception as e:
            self.central_conn.logger.error(f"Error in scope get method: {e}")
            return False

    def get_all_sites(self):
        """Performs GET calls to retrieve all the sites from Central.

        Returns:
            (list): List of Site objects

        Raises:
            Exception: If sites cannot be fetched from Central
        """
        sites_response = get_all_scope_elements(obj=self, scope="site")
        if not sites_response:
            raise Exception(
                "Failed to fetch sites from Central. Sites are a required construct of new Central. Please check your Central account & ensure that you have at least one site created."
            )
        self.sites = [
            Site(
                central_conn=self.central_conn,
                site_attributes=site,
                from_api=True,
            )
            for site in sites_response
        ]
        return self.sites

    def get_all_site_collections(self):
        """Performs GET calls to retrieve all the site collections from Central.

        Returns:
            (list): List of Site_Collection objects
        """
        site_collections_response = get_all_scope_elements(
            obj=self, scope="site_collection"
        )

        self.site_collections = [
            Site_Collection(
                central_conn=self.central_conn,
                collection_attributes=collection,
                from_api=True,
            )
            for collection in site_collections_response
        ]
        return self.site_collections

    def get_all_devices(self):
        """Performs GET calls to retrieve all the devices from Central.

        Returns:
            (list): List of Device objects
        """
        device_list = Device.get_all_devices(central_conn=self.central_conn)
        self.devices = [
            Device(
                central_conn=self.central_conn,
                device_attributes=device,
                from_api=True,
            )
            for device in device_list
        ]
        self.central_conn.logger.info(
            f"Total devices fetched from account: {len(self.devices)}"
        )
        return self.devices

    def get_all_device_groups(self):
        """Performs GET calls to retrieve all the device groups from Central.

        Returns:
            (list): List of Device_Group objects
        """
        device_groups_list = get_all_scope_elements(
            obj=self, scope="device_group"
        )
        self.device_groups = [
            Device_Group(
                central_conn=self.central_conn,
                device_group_attributes=device_group,
                from_api=True,
            )
            for device_group in device_groups_list
        ]
        return self.device_groups

    def get_id(self):
        """Returns the ID of the Global scope.

        If the ID hasn't been set, it is fetched from Central (GET global).

        Returns:
            (int or None): ID of global scope, or None if unable to fetch
        """
        if self.id is None:
            resp = self.central_conn.command(
                api_method="GET", api_path=generate_url(SCOPE_URLS["GLOBAL"])
            )
            if resp["code"] == 200:
                self.id = int(resp["msg"]["scopeId"])
                self.central_conn.logger.info(
                    "Global scope ID set successfully."
                )
            else:
                self.central_conn.logger.error(
                    f"Unable to get global scope ID. Error message - {resp['msg']}"
                )
        return self.id

    def get_sites(
        self, limit=DEFAULT_LIMIT, offset=0, filter_field="", sort=""
    ):
        """Fetches the list of sites from Central based on the provided attributes.

        Args:
            limit (int): Number of sites to be fetched, defaults to 100
            offset (int): Pagination start index, defaults to 0
            filter_field (str): Field for sorting. Accepted values: scopeName,
                address, city, state, country, zipcode, collectionName
            sort (str): Direction of sorting. Accepted values: scopeName,
                address, state, country, city, deviceCount, collectionName,
                zipcode, timezone, longitude, latitude

        Returns:
            (list or None): List of sites based on the provided arguments, None if errors occur
        """
        return get_scope_elements(
            obj=self,
            scope="site",
            limit=limit,
            offset=offset,
            filter_field=filter_field,
            sort=sort,
        )

    def get_site_collections(
        self,
        limit=DEFAULT_LIMIT,
        offset=0,
        filter_field="",
        sort="",
    ):
        """Fetches the list of site collections from Central based on the provided attributes.

        Args:
            limit (int): Number of site collections to be fetched, defaults to 100
            offset (int): Pagination start index, defaults to 0
            filter_field (str): Field for sorting. Accepted values: scopeName,
                description
            sort (str): Direction of sorting. Accepted values: scopeName,
                description, deviceCount, siteCount



        Returns:
            (list or None): List of site collections based on the provided arguments, None if errors occur
        """
        return get_scope_elements(
            obj=self,
            scope="site_collection",
            limit=limit,
            offset=offset,
            filter_field=filter_field,
            sort=sort,
        )

    def _correlate_scopes(self):
        """Rebuilds lookup maps and correlates sites with site collections and devices with sites & device groups."""
        self._update_lookup_map()
        for site_collection in self.site_collections:
            site_collection.sites = []
        for element in self.sites + self.device_groups:
            element.devices = []

        for site in self.sites:
            collection_id = getattr(site, "site_collection_id", None)
            if collection_id and int(collection_id) in self._lookup_maps["id"]:
                self._lookup_maps["id"][int(collection_id)].add_site(
                    site.get_id()
                )

        for device in self.devices:
            site_id = getattr(device, "site_id", None)
            if site_id and int(site_id) in self._lookup_maps["id"]:
                self._lookup_maps["id"][int(site_id)].devices.append(
                    device.get_id()
                )
            group_id = getattr(device, "group_id", None)
            if group_id and int(group_id) in self._lookup_maps["id"]:
                self._lookup_maps["id"][int(group_id)].devices.append(
                    device.get_id()
                )

    def find_site_collection(
        self, site_collection_ids=None, site_collection_names=None
    ):
        """Returns the site collection based on the provided parameters.

        Only one of site_collection_ids or site_collection_names is required.

        Args:
            site_collection_ids (int or list, optional): ID(s) of site collections to find
            site_collection_names (str or list, optional): Name(s) of site collections to find

        Returns:
            (Site_Collection or list or None): Found site collection(s) or None if not found
        """
        return self._find_or_refresh(
            self.get_all_site_collections,
            ids=site_collection_ids,
            names=site_collection_names,
            scope="site_collection",
        )

    def find_site(self, site_ids=None, site_names=None):
        """Returns the site based on the provided parameters.

        Only one of site_ids or site_names is required.

        Args:
            site_ids (int or list, optional): ID(s) of site to find
            site_names (str or list, optional): Name(s) of site to find

        Returns:
            (Site or list or None): Found site(s) or None if not found
        """
        return self._find_or_refresh(
            self.get_all_sites, ids=site_ids, names=site_names, scope="site"
        )

    def find_device(
        self, device_ids=None, device_names=None, device_serials=None
    ):
        """Returns the device based on the provided parameters.

        Only one of device_ids, device_names, or device_serials is required.

        Args:
            device_ids (int or list, optional): ID(s) of devices to find
            device_names (str or list, optional): Name(s) of devices to find
            device_serials (str or list, optional): Serial number(s) of devices to find

        Returns:
            (Device or list or None): Found device(s) or None if not found
        """
        return self._find_or_refresh(
            self.get_all_devices,
            ids=device_ids,
            names=device_names,
            serials=device_serials,
            scope="device",
        )

    def find_device_group(
        self,
        device_group_ids=None,
        device_group_names=None,
    ):
        """Returns the device group based on the provided parameters.

        Only one of device_group_ids or device_group_names is required.

        Args:
            device_group_ids (int or list, optional): ID(s) of device groups to find
            device_group_names (str or list, optional): Name(s) of device groups to find

        Returns:
            (Device_Group or list or None): Found device group(s) or None if not found
        """
        return self._find_or_refresh(
            self.get_all_device_groups,
            ids=device_group_ids,
            names=device_group_names,
            scope="device_group",
        )

    def _find_or_refresh(self, refresh, **kwargs):
        """Finds scope elements; on a miss re-fetches that scope from Central,
        re-correlates and retries once.

        Args:
            refresh (callable): Method that re-fetches the scope's elements
            **kwargs: Arguments for _find_scope_element

        Returns:
            (object or list or None): Found element(s) or None if not found
        """
        found = self._find_scope_element(**kwargs)
        if not found:
            refresh()
            self._correlate_scopes()
            found = self._find_scope_element(**kwargs)
        return found

    def _find_scope_element(self, ids=None, names=None, serials=None, scope=""):
        """Helper function to find scope elements based on provided parameters.

        Args:
            ids (int or list, optional): ID(s) of the element(s)
            names (str or list, optional): Name(s) of the element(s)
            serials (str or list, optional): Serial number(s) of the element(s) (only for devices)
            scope (str, optional): Specific scope to search in (e.g., "site", "device")

        Returns:
            (list or None): Found element(s) or None if not found
        """
        # Validate input parameters
        validate_find_scope_elements(
            ids=ids, names=names, serials=serials, scope=scope
        )
        self._update_lookup_map()
        result = self._search_scope_elements(ids, names, serials, scope)

        if not result:
            params = [("ids", ids), ("names", names), ("serials", serials)]
            param_type, param_value = next(
                ((k, v) for k, v in params if v), ("unknown", None)
            )

            self.central_conn.logger.error(
                f"Unable to find scope element for scope '{scope}'. Parameter: {param_type}={param_value}. Please check the provided parameter(s)."
            )
            result = None

        return result

    def _search_scope_elements(
        self, ids=None, names=None, serials=None, scope=""
    ):
        """Searches for scope elements using the lookup maps.

        Args:
            ids (int or list, optional): ID(s) of the element(s)
            names (str or list, optional): Name(s) of the element(s)
            serials (str or list, optional): Serial number(s) of the element(s) (only for devices)
            scope (str, optional): Specific scope to search in (e.g., "site", "device")

        Returns:
            (list or None): Found element(s) or None if not found
        """
        found_elements = None
        if ids:
            found_elements = lookup_in_map(ids, self._lookup_maps["id"])
        elif serials:
            found_elements = lookup_in_map(serials, self._lookup_maps["serial"])
        elif names:
            self._update_name_lookup_map()
            if scope:
                scope = scope.lower()
                found_elements = lookup_in_map(
                    names, self._lookup_maps["name"][scope + "s"]
                )
            else:
                # If no scope is provided, check all scopes
                for scope in SUPPORTED_SCOPES:
                    found_elements = lookup_in_map(
                        names, self._lookup_maps["name"][scope + "s"]
                    )
                    if found_elements:
                        break
        return found_elements

    def _update_name_lookup_map(self):
        """Updates the name lookup map for all supported scopes."""
        for scope in SUPPORTED_SCOPES:
            self._lookup_maps["name"][scope + "s"] = {
                element.get_name(): element
                for element in getattr(self, scope + "s", [])
            }

    def _update_lookup_map(self):
        """Rebuilds the lookup maps for IDs and serials from the current scope lists."""
        self._lookup_maps["id"] = {
            element.get_id(): element
            for element in self.sites
            + self.site_collections
            + self.devices
            + self.device_groups
        }
        if self.id is not None:
            self._lookup_maps["id"][self.id] = self
        self._lookup_maps["serial"] = {
            device.get_serial(): device for device in self.devices
        }

    def add_sites_to_site_collection(
        self,
        site_collection_id=None,
        site_collection_name=None,
        site_ids=None,
        site_names=None,
    ):
        """Adds site(s) to a site collection.

        Args:
            site_collection_id (int, optional): ID of the site collection.
                Either site_collection_name or site_collection_id is required.
            site_collection_name (str, optional): Name of the site collection.
                Either site_collection_name or site_collection_id is required.
            site_ids (int or list, optional): ID(s) of the site(s) to associate.
                Either site_ids or site_names is required.
            site_names (str or list, optional): Name(s) of the site(s) to associate.
                Either site_ids or site_names is required.

        Returns:
            (bool): True if successful, False otherwise
        """
        site_collection = self.find_site_collection(
            site_collection_ids=site_collection_id,
            site_collection_names=site_collection_name,
        )
        if site_collection:
            sites = self.find_site(site_ids=site_ids, site_names=site_names)
            if isinstance(sites, Site):
                sites = [sites]
            if all(sites):
                site_association = site_collection.associate_site(sites=sites)
                if site_association:
                    return True
                else:
                    self.central_conn.logger.error(
                        "Unable to complete site association with site collection."
                    )
                    return False

            else:
                self.central_conn.logger.error(
                    "Unable to associate invalid site(s) with site collection. Please provide valid site id(s) or name(s)."
                )
                return False
        elif site_collection is None:
            self.central_conn.logger.error(
                "Unable to associate site(s) with invalid site collection. Please provide a valid site collection id or name."
            )
            return False

    def remove_sites_from_site_collection(self, site_ids=None, site_names=None):
        """Removes site(s) from a site collection.

        Args:
            site_ids (int or list, optional): ID(s) of the site(s) to unassociate.
                Either site_ids or site_names is required.
            site_names (str or list, optional): Name(s) of the site(s) to unassociate.
                Either site_ids or site_names is required.

        Returns:
            (bool): True if successful, False otherwise
        """
        sites = self.find_site(site_ids=site_ids, site_names=site_names)
        if not isinstance(sites, list):
            sites = [sites]
        if all(sites):
            api_method = "DELETE"
            api_path = generate_url(SCOPE_URLS["REMOVE_SITE_FROM_COLLECTION"])
            api_params = {
                "site-id": ",".join(str(site.get_id()) for site in sites)
            }
            resp = self.central_conn.command(
                api_method=api_method, api_path=api_path, api_params=api_params
            )
            if resp["code"] == 200:
                site_name_str = ", ".join(
                    [str(site.get_name()) for site in sites]
                )
                self.central_conn.logger.info(
                    "Successfully removed sites "
                    + site_name_str
                    + " from site collection."
                )
                self._update_site_collection_attributes(sites=sites)
                return True
            else:
                self.central_conn.logger.error(resp["msg"])
                return False
        else:
            self.central_conn.logger.error(
                "Unable to remove invalid site(s) from site collection. Please provide valid site id(s) or name(s)."
            )
        return False

    def _update_site_collection_attributes(self, sites):
        """Helper function to update site collection attributes after removing sites.

        Args:
            sites (list): List of Site objects to update
        """
        for site in sites:
            old_collection_attributes = site.get_site_collection_attributes()
            if old_collection_attributes is not None:
                old_collection = self.find_site_collection(
                    site_collection_ids=old_collection_attributes["id"]
                )
                if old_collection:
                    old_collection.remove_site(site_id=site.get_id())
                site.remove_site_collection()

    def create_site(
        self,
        site_attributes,
        site_collection_id=None,
        site_collection_name=None,
    ):
        """Creates a new site in Central and optionally associates it with a site collection.

        Args:
            site_attributes (dict): Attributes of the site to create
            site_collection_id (int, optional): ID of the site collection.
                Either site_collection_name or site_collection_id is required if associating.
            site_collection_name (str, optional): Name of the site collection.
                Either site_collection_name or site_collection_id is required if associating.

        Returns:
            (bool): True if successful, False otherwise
        """
        site_obj = Site(
            site_attributes=site_attributes, central_conn=self.central_conn
        )
        site_creation_status = site_obj.create()

        if site_creation_status:
            self.sites.append(site_obj)
            if site_collection_id or site_collection_name:
                self.add_sites_to_site_collection(
                    site_collection_id=site_collection_id,
                    site_collection_name=site_collection_name,
                    site_ids=[site_obj.get_id()],
                )

        else:
            self.central_conn.logger.error(
                f"Unable to create site {site_obj.get_name()}"
            )
        return site_creation_status

    def delete_site(self, site_id=None, site_name=None):
        """Deletes a site in Central.

        Args:
            site_id (int, optional): ID of the site to delete.
                Either site_id or site_name is required.
            site_name (str, optional): Name of the site to delete.
                Either site_id or site_name is required.

        Returns:
            (bool): True if successful, False otherwise
        """
        site_deletion_status = False
        site = self.find_site(site_ids=site_id, site_names=site_name)
        if site:
            site_id = site.get_id()
            site_deletion_status = site.delete()
            if site_deletion_status:
                self._remove_scope_element(scope="site", element_id=site_id)
                if site.site_collection_id:
                    site_collection = self.find_site_collection(
                        site_collection_ids=site.site_collection_id
                    )
                    if site_collection:
                        site_collection.remove_site(site_id)
        else:
            self.central_conn.logger.error(
                "Please provide a valid site id or name to be deleted."
            )
        return site_deletion_status

    def _remove_scope_element(self, scope, element_id):
        """Removes a scope element from the internal list.

        Args:
            scope (str): Type of the element (e.g., site, site_collection)
            element_id (int): ID of the element to remove

        Returns:
            (bool): True if successful, False otherwise
        """
        element_list = getattr(self, scope + "s")
        for index, element in enumerate(element_list):
            if element.get_id() == element_id:
                element_list.pop(index)
                return True
        return False

    def create_site_collection(
        self, collection_attributes, site_ids=None, site_names=None
    ):
        """Creates a new site collection in Central and optionally associates sites with it.

        Args:
            collection_attributes (dict): Attributes of the site collection to create
            site_ids (int or list, optional): ID(s) of the site(s) to associate.
                Either site_ids or site_names is required if associating.
            site_names (str or list, optional): Name(s) of the site(s) to associate.
                Either site_ids or site_names is required if associating.

        Returns:
            (bool): True if successful, False otherwise
        """
        site_collection_obj = Site_Collection(
            collection_attributes=collection_attributes,
            central_conn=self.central_conn,
        )
        site_collection_creation_status = site_collection_obj.create()
        if site_collection_creation_status:
            self.site_collections.append(site_collection_obj)
            if site_ids or site_names:
                site_addition_status = self.add_sites_to_site_collection(
                    site_collection_id=site_collection_obj.get_id(),
                    site_ids=site_ids,
                    site_names=site_names,
                )
                if site_addition_status:
                    self.central_conn.logger.info(
                        f"Successfully associated sites with site collection {site_collection_obj.get_name()}"
                    )
                else:
                    self.central_conn.logger.error(
                        f"Failed to associate sites with site collection {site_collection_obj.get_name()}"
                    )
        else:
            self.central_conn.logger.error(
                f"Unable to create site collection {site_collection_obj.get_name()}"
            )
        return site_collection_creation_status

    def delete_site_collection(
        self,
        site_collection_id=None,
        site_collection_name=None,
        remove_sites=False,
    ):
        """Deletes a site collection in Central.

        Optionally removes associated sites first.

        Args:
            site_collection_id (int, optional): ID of the site collection to delete.
                Either site_collection_id or site_collection_name is required.
            site_collection_name (str, optional): Name of the site collection to delete.
                Either site_collection_id or site_collection_name is required.
            remove_sites (bool): If True, removes sites associated with the site collection
                before deleting it. If False and sites are associated, deletion will fail.

        Returns:
            (bool): True if successful, False otherwise
        """
        site_collection_deletion_status = False
        site_collection = self.find_site_collection(
            site_collection_ids=site_collection_id,
            site_collection_names=site_collection_name,
        )
        if site_collection:
            num_associated_sites = len(site_collection.sites)
            if remove_sites is False and num_associated_sites > 0:
                self.central_conn.logger.error(
                    "Unable to delete site collection with "
                    f"{num_associated_sites} sites associated with it. "
                    "Set remove_sites argument to True to remove sites associated with site collection before deleting it."
                )
                return site_collection_deletion_status
            elif remove_sites and num_associated_sites > 0:
                self.central_conn.logger.info(
                    f"Attempting to remove {num_associated_sites} associated sites before deleting site collection "
                    + site_collection.get_name()
                )
                site_unassociated_status = (
                    self.remove_sites_from_site_collection(
                        site_ids=site_collection.sites
                    )
                )
                if site_unassociated_status is not True:
                    self.central_conn.logger.info(
                        f"Unable to remove {num_associated_sites} associated sites from site collection "
                        + f"{site_collection.get_name()}."
                    )
                    return site_unassociated_status
            site_collection_id = site_collection.get_id()
            site_collection_deletion_status = site_collection.delete()
            if site_collection_deletion_status:
                self._remove_scope_element(
                    scope="site_collection", element_id=site_collection_id
                )
        else:
            self.central_conn.logger.error(
                "Please provide a valid site collection id or name to be deleted."
            )
        return site_collection_deletion_status

    def get_hierarchy(self, scope, id=None, name=None):
        """Fetches the hierarchy of the specified scope element in the global hierarchy.

        Args:
            scope (str): Type of the element (e.g., site, site_collection, device, device_group)
            id (int, optional): ID of the element
            name (str, optional): Name of the element

        Returns:
            (dict or None): Hierarchy of the specified element, None if unable to fetch
        """
        if not is_supported_scope(self, scope):
            return None

        scope_id = None
        if id:
            scope_id = id
        else:
            if scope == "site":
                site = self.find_site(site_names=name)
                if site is not None:
                    scope_id = site.get_id()
            elif scope == "site_collection":
                site_collection = self.find_site_collection(
                    site_collection_names=name
                )
                if site_collection is not None:
                    scope_id = site_collection.get_id()
            if not scope_id:
                self.central_conn.logger.error(
                    f"Unable to find id of specified scope element with name of {name}"
                )
                return None

        api_method = "GET"
        api_path = generate_url(SCOPE_URLS["HIERARCHY"])
        # v1 hierarchy types verified live; device groups are "device_collection"
        hierarchy_type = {"device_group": "device_collection"}.get(scope, scope)
        api_params = {"id": str(scope_id), "type": hierarchy_type}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_params=api_params
        )
        if resp["code"] == 200:
            self.central_conn.logger.info(
                f"Successfully fetched scope hierarchy of {scope} with id {scope_id}"
            )
            return resp["msg"]["items"]
        else:
            self.central_conn.logger.error(
                f"Unable to fetch scope hierarchy of {scope} with id {scope_id}. Error message - {resp['msg']}"
            )
            return None

    def __str__(self):
        """Returns a string representation of the Global scope.

        Returns:
            (str): String representation of the Global scope
        """
        return f"Global ID - {self.id}"

    def get_scope_profiles(self):
        """Fetches all profile assignments and records them on the matching scope elements.

        Library assignments come from config-assignments; scope-map rows not
        among them are local profiles. Each entry's object_type is "LIBRARY"
        or "LOCAL".
        """
        assignments = get_config_assignments(central_conn=self.central_conn)
        if assignments is None:
            self.central_conn.logger.error(
                "Unable to fetch config assignments; assigned profiles left unchanged"
            )
            return
        self.central_conn.logger.info(
            f"Total config assignments fetched from account: {len(assignments)}"
        )
        library = [
            (
                int(a["scope-id"]),
                a["device-function"],
                f"{a['profile-type']}/{a['profile-instance']}",
            )
            for a in assignments
        ]
        # ponytail: local profiles come from deprecated scope-maps (config-assignments has no local view); switch when Central adds one
        scope_maps = get_scope_maps(central_conn=self.central_conn)
        if scope_maps is None:
            self.central_conn.logger.warning(
                "Unable to fetch scope maps; local profiles could not be loaded"
            )
            scope_maps = []
        library_keys = set(library)
        local = [
            (int(m["scope-id"]), m["persona"], m["resource"]) for m in scope_maps
        ]
        local = [row for row in local if row not in library_keys]
        for element in self._lookup_maps["id"].values():
            element.assigned_profiles = []
        for object_type, rows in (("LIBRARY", library), ("LOCAL", local)):
            for scope_id, device_function, resource in rows:
                element = self._lookup_maps["id"].get(scope_id)
                if element is not None:
                    element.add_profile(
                        name=resource,
                        device_function=device_function,
                        object_type=object_type,
                    )

    def assign_profile_to_scope(
        self,
        profile_name,
        profile_persona=None,  # remove persona in 2.x
        scope=None,
        scope_name=None,
        scope_id=None,
        *,
        device_function=None,
    ):
        """Assigns a configuration profile to the specified scope (config-assignments API).

        Args:
            profile_name (str): Profile resource string
                "<profile-type>/<profile-instance>", e.g. "layer2-vlan/100".
            profile_persona (str, optional): Deprecated alias of device_function.
            scope (str, optional): Type of the scope (e.g., global, site, site_collection, device)
            scope_name (str, optional): Name of the scope element.
                Either scope_name or scope_id is required.
            scope_id (int, optional): ID of the scope element.
                Either scope_name or scope_id is required.
            device_function (str, optional): Device function of the profile,
                e.g. "CAMPUS_AP" or "ALL". Optional if assigning to a device.

        Returns:
            (bool): True if successful, False otherwise
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=profile_persona
        )
        element = self._profile_scope_element(scope, scope_name, scope_id)
        return bool(element) and element.assign_profile(
            profile_name, device_function=device_function
        )

    def unassign_profile_to_scope(
        self,
        profile_name,
        profile_persona=None,  # remove persona in 2.x
        scope=None,
        scope_name=None,
        scope_id=None,
        *,
        device_function=None,
    ):
        """Unassigns a configuration profile from the specified scope (config-assignments API).

        Args:
            profile_name (str): Profile resource string
                "<profile-type>/<profile-instance>", e.g. "layer2-vlan/100".
            profile_persona (str, optional): Deprecated alias of device_function.
            scope (str, optional): Type of the scope (e.g., global, site, site_collection, device)
            scope_name (str, optional): Name of the scope element.
                Either scope_name or scope_id is required.
            scope_id (int, optional): ID of the scope element.
                Either scope_name or scope_id is required.
            device_function (str, optional): Device function of the profile.
                Optional if unassigning from a device.

        Returns:
            (bool): True if successful, False otherwise
        """
        # remove persona in 2.x
        device_function = _resolve_device_function(
            device_function=device_function, persona=profile_persona
        )
        element = self._profile_scope_element(scope, scope_name, scope_id)
        return bool(element) and element.unassign_profile(
            profile_name, device_function=device_function
        )

    def _profile_scope_element(self, scope, scope_name, scope_id):
        """Returns the scope element a profile is (un)assigned to.

        Args:
            scope (str): Type of the scope; "global" returns this object
            scope_name (str): Name of the scope element
            scope_id (int): ID of the scope element

        Returns:
            (object or None): Scope element, or None if not found
        """
        if scope == "global":
            return self
        return self._find_scope_element(
            names=scope_name, ids=scope_id, scope=scope
        )

    def move_devices_between_sites(
        self,
        current_site,
        new_site,
        device_serial,
        device_type=None,
        device_identifier=None,
        deployment_mode=None,
    ):
        """Deprecated: moving devices between sites via NBAPI is not supported.

        Emits a DeprecationWarning and always returns False.

        Args:
            current_site (int or str or Site): ID, name, or Site instance of the current site
            new_site (int or str or Site): ID, name, or Site instance of the destination site
            device_serial (str): Serial number of device to move
            device_type (str, optional): Type of device. For example: AP, SWITCH, GATEWAY
            device_identifier (str, optional): Additional device identifier
            deployment_mode (str, optional): Deployment type. For example: Standalone, Virtual Controller

        Returns:
            (bool): True if successful, False otherwise
        """
        _warn_deprecated(
            "move_devices_between_sites is deprecated: moving devices between sites via NBAPI is not supported. It always returns False."
        )
        return False
