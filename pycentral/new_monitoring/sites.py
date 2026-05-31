from ..utils.monitoring_utils import execute_get, simplified_site_resp
from ..exceptions import ParameterError
from .constants import SITE_LIMIT

# Sites doesn't really abide by the same pattern as other monitor types
# Should we keep?
MONITOR_TYPE = "sites"


class MonitoringSites:
    @staticmethod
    def get_all_sites(central_conn, return_raw_response=False):
        """
        Retrieve all sites information including health details, handling pagination.

        Args:
            central_conn (NewCentralBase): Central connection object.
            return_raw_response (bool, optional): If True, return the raw API payloads. Defaults to False.

        Returns:
            (list[dict]): List of site records. If return_raw_response is False, each site response is simplified via simplified_site_resp.
        """
        sites = []
        total_sites = None
        limit = SITE_LIMIT
        offset = 0
        while True:
            response = MonitoringSites.get_sites(
                central_conn, limit=limit, offset=offset
            )
            if total_sites is None:
                total_sites = response.get("total", 0)
            sites.extend(response["items"])
            if len(sites) == total_sites:
                break
            offset += limit
        if not return_raw_response:
            sites = [simplified_site_resp(site) for site in sites]
        return sites

    @staticmethod
    def get_sites(central_conn, limit=SITE_LIMIT, offset=0):
        """
        Retrieve a single page of site health information. It returns details such as devices, clients, critical alerts with count, along with their respective health and health reasons for each site.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/sites-health`

        Args:
            central_conn (NewCentralBase): Central connection object.
            limit (int, optional): Number of entries to return (default is 100).
            offset (int, optional): Number of entries to skip for pagination (default is 0).

        Returns:
            (dict): Raw API response for the requested page (typically contains 'items' and 'total').
        """
        params = {"limit": limit, "offset": offset}
        path = "sites-health"
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def list_sites_device_health(central_conn, limit=100, offset=0):
        """
        Retrieve per-site device health statistics. It returns the number of poor, fair, and good performing devices for each site.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/sites-device-health`

        Args:
            central_conn (NewCentralBase): Central connection object.
            limit (int, optional): Number of entries to return (default is 100).
            offset (int, optional): Number of entries to skip for pagination (default is 0).

        Returns:
            (dict): Raw API response containing device health counts per site.
        """
        params = {"limit": limit, "offset": offset}
        path = "sites-device-health"
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def list_site_information(central_conn, site_id):
        """
        Retrieve detailed health information for a specific site. It returns details such as devices, clients, critical alerts with count, along with their respective health and health reasons.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/site-health/{site_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (int): Identifier of the site to query.

        Returns:
            (dict): Raw API response with site health details.

        Raises:
            ParameterError: If site_id is missing or not an integer.
        """
        if not site_id or not isinstance(site_id, int):
            raise ParameterError("site_id is required and must be an integer")
        path = f"site-health/{site_id}"
        return execute_get(central_conn, endpoint=path)
