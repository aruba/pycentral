from ..utils.monitoring_utils import (
    execute_get,
    get_all_pages,
    validate_limit_and_next,
    validate_query_length,
    validate_serial_query,
    validate_site_id,
)
from .constants import WLAN_LIMIT


class WLAN:
    @staticmethod
    def get_all_wlans(
        central_conn,
        site_id=None,
        serial_number=None,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all WLANs associated to a customer, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/wlans`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str, optional): Site identifier to filter WLANs.
            serial_number (str, optional): Serial number of an AP to filter WLANs.
            filter_str (str, optional): Optional filter expression for the WLAN list.
            sort (str, optional): Optional sort expression for the WLAN list.

        Returns:
            (list[dict]): List of WLAN items.
        """
        return get_all_pages(
            WLAN.get_wlans,
            limit=WLAN_LIMIT,
            central_conn=central_conn,
            site_id=site_id,
            serial_number=serial_number,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_wlans(
        central_conn,
        site_id=None,
        serial_number=None,
        filter_str=None,
        sort=None,
        limit=WLAN_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a list of WLANs associated to a customer.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/wlans`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str, optional): ID of the Site for which WLAN information is requested. Max length 128.
            serial_number (str, optional): Serial number of an access point device. Max length 16.
            filter_str (str, optional): OData Version 4.0 filter string (limited functionality). 
                Supports only 'and' conjunction ('or' and 'not' are NOT supported). 
                Supported field: band (operators: eq, in). Max length 256.
            sort (str, optional): Comma separated list of sort expressions. Supported fields: 
                wlanName, band, status, securityLevel, security, vlan, primaryUsage. Max length 256.
            limit (int, optional): Maximum number of WLANs to return (0-1000, default is 1000).
            next_page (int, optional): Pagination cursor for next page (default is 1).

        Returns:
            (dict): API response containing:
                - items (list): List of WLAN dictionaries with fields like wlanName, primaryUsage,
                    securityLevel, security, band, status, vlan, id, type.
                - count (int): Number of WLANs in current response.
                - total (int): Total number of WLANs matching the criteria.
                - next (str|None): Pagination cursor for the next page.

        Raises:
            ParameterError: If limit exceeds 1000 or next_page is less than 1.
            ParameterError: If site_id exceeds 128 characters.
            ParameterError: If serial_number exceeds 16 characters.
            ParameterError: If filter_str exceeds 256 characters.
            ParameterError: If sort exceeds 256 characters.
        """
        validate_limit_and_next(limit, next_page, WLAN_LIMIT)
        validate_site_id(site_id)
        validate_serial_query(serial_number)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint="wlans",
            params={
                "site-id": site_id,
                "serial-number": serial_number,
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )
   