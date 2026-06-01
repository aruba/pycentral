from ..exceptions import ParameterError
from ..utils.monitoring_utils import (
    build_trend_params,
    execute_get,
    get_all_pages,
    normalize_metric,
    normalize_trend_response,
    validate_central_conn_and_serial,
    validate_limit_and_next,
    validate_query_length,
    validate_required_value,
    validate_site_id,
)
from .constants import AP_LIMIT, BSSID_LIMIT, RADIO_LIMIT, SWARM_LIMIT, TUNNEL_LIMIT

MONITOR_TYPE = "aps"

AP_TREND_METRICS = {
    "throughput": "throughput-trends",
    "cpu-utilization": "cpu-utilization-trends",
    "memory-utilization": "memory-utilization-trends",
    "power-consumption": "power-consumption-trends",
}
RADIO_TREND_METRICS = {
    "throughput": "throughput-trends",
    "channel-utilization": "channel-utilization-trends",
    "channel-quality": "channel-quality-trends",
    "noise-floor": "noise-floor-trends",
    "frames": "frames-trends",
}
PORT_TREND_METRICS = {
    "throughput": "throughput-trends",
    "frames": "frames-trends",
    "crc": "crc-trends",
    "collisions": "collisions-trends",
}
TUNNEL_TREND_METRICS = {
    "throughput": "throughput-trends",
    "packet-loss": "packet-loss-trends",
    "mos": "mos-trends",
    "jitter": "jitter-trends",
    "latency": "latency-trends",
}
AP_INTERFACE_TYPES = {"WIRED", "WIRELESS", "LTE"}


class MonitoringAPs:

    @staticmethod
    def get_all_aps(central_conn, filter_str=None, sort=None):
        """
        Retrieve all access points (APs), handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/aps`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of AP items.
        """
        return get_all_pages(
            MonitoringAPs.get_aps,
            limit=AP_LIMIT,
            central_conn=central_conn,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_aps(
        central_conn, filter_str=None, sort=None, limit=AP_LIMIT, next_page=1
    ):
        """
        Retrieve a single page of APs.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/aps`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 1000).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the aps endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If limit or next_page values are invalid.
        """
        validate_limit_and_next(limit, next_page, AP_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint=MONITOR_TYPE,
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_ap_details(central_conn, serial_number):
        """
        Get details for a specific AP.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/aps/{serial_number}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.

        Returns:
            (dict): API response with AP details.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        return execute_get(central_conn, endpoint=f"{MONITOR_TYPE}/{serial_number}")

    @staticmethod
    def _execute_trend_request(
        central_conn,
        serial_number,
        metric,
        metric_map,
        resource_path=None,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        extra_params=None,
        return_raw_response=False,
    ):
        validate_central_conn_and_serial(central_conn, serial_number)
        metric = normalize_metric(metric, metric_map)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            extra_params=extra_params,
        )
        path = f"{MONITOR_TYPE}/{serial_number}"
        if resource_path:
            path = f"{path}/{resource_path}"
        path = f"{path}/{metric_map[metric]}"
        response = execute_get(central_conn, endpoint=path, params=params)
        return normalize_trend_response(response, return_raw_response)

    @staticmethod
    def get_ap_trends(
        central_conn,
        serial_number,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        interface_type="WIRELESS",
        return_raw_response=False,
    ):
        """
        Retrieve trend data for an AP metric.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/aps/{serial_number}/throughput-trends`
        `GET network-monitoring/v1/aps/{serial_number}/cpu-utilization-trends`
        `GET network-monitoring/v1/aps/{serial_number}/memory-utilization-trends`
        `GET network-monitoring/v1/aps/{serial_number}/power-consumption-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.
            metric (str): Trend metric to retrieve. Supported values are `throughput`, `cpu-utilization`, `memory-utilization`, and `power-consumption`.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string or seconds for relative queries.
            site_id (str, optional): Site identifier to scope the trend request.
            interface_type (str, optional): Interface type for throughput requests. Supported values are `WIRED`, `WIRELESS`, and `LTE`.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, metric, or interface_type is invalid.
        """
        extra_params = None
        normalized_metric = normalize_metric(metric, AP_TREND_METRICS)
        if normalized_metric == "throughput":
            normalized_interface_type = str(interface_type).upper()
            if normalized_interface_type not in AP_INTERFACE_TYPES:
                supported = ", ".join(sorted(AP_INTERFACE_TYPES))
                raise ParameterError(
                    "interface_type must be one of "
                    f"{supported} for AP throughput trends"
                )
            extra_params = {"interface-type": normalized_interface_type}

        return MonitoringAPs._execute_trend_request(
            central_conn=central_conn,
            serial_number=serial_number,
            metric=normalized_metric,
            metric_map=AP_TREND_METRICS,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            extra_params=extra_params,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_all_radios(central_conn, filter_str=None, sort=None):
        """
        Retrieve all fleet radios, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/radios`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression for the radio list.
            sort (str, optional): Optional sort expression for the radio list.

        Returns:
            (list[dict]): List of radio items.
        """
        return get_all_pages(
            MonitoringAPs.get_radios,
            limit=RADIO_LIMIT,
            central_conn=central_conn,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_radios(
        central_conn, filter_str=None, sort=None, limit=RADIO_LIMIT, next_page=1
    ):
        """
        Retrieve a single page of fleet radios.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/radios`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression for the radio list.
            sort (str, optional): Optional sort expression for the radio list.
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for the next page.

        Returns:
            (dict): API response for the radios endpoint.

        Raises:
            ParameterError: If limit, next_page, filter_str, or sort is invalid.
        """
        validate_limit_and_next(limit, next_page, RADIO_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint="radios",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_all_bssids(central_conn, filter_str=None, sort=None):
        """
        Retrieve all fleet BSSIDs, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/bssids`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression for the BSSID list.
            sort (str, optional): Optional sort expression for the BSSID list.

        Returns:
            (list[dict]): List of BSSID items.
        """
        return get_all_pages(
            MonitoringAPs.get_bssids,
            limit=BSSID_LIMIT,
            central_conn=central_conn,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_bssids(
        central_conn, filter_str=None, sort=None, limit=BSSID_LIMIT, next_page=1
    ):
        """
        Retrieve a single page of fleet BSSIDs.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/bssids`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression for the BSSID list.
            sort (str, optional): Optional sort expression for the BSSID list.
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for the next page.

        Returns:
            (dict): API response for the bssids endpoint.

        Raises:
            ParameterError: If limit, next_page, filter_str, or sort is invalid.
        """
        validate_limit_and_next(limit, next_page, BSSID_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint="bssids",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_all_swarms(central_conn, filter_str=None, sort=None):
        """
        Retrieve all swarms, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/swarms`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression for the swarm list.
            sort (str, optional): Optional sort expression for the swarm list.

        Returns:
            (list[dict]): List of swarm items.
        """
        return get_all_pages(
            MonitoringAPs.get_swarms,
            limit=SWARM_LIMIT,
            central_conn=central_conn,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_swarms(
        central_conn, filter_str=None, sort=None, limit=SWARM_LIMIT, next_page=1
    ):
        """
        Retrieve a single page of swarms.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/swarms`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression for the swarm list.
            sort (str, optional): Optional sort expression for the swarm list.
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for the next page.

        Returns:
            (dict): API response for the swarms endpoint.

        Raises:
            ParameterError: If limit, next_page, filter_str, or sort is invalid.
        """
        validate_limit_and_next(limit, next_page, SWARM_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint="swarms",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_swarm_details(central_conn, cluster_id):
        """
        Get details for a specific swarm.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/swarms/{cluster_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_id (str): Cluster identifier for the swarm.

        Returns:
            (dict): API response with swarm details.

        Raises:
            ParameterError: If cluster_id is missing.
        """
        validate_required_value("cluster_id", cluster_id)
        return execute_get(central_conn, endpoint=f"swarms/{cluster_id}")

    @staticmethod
    def get_ap_radios(central_conn, serial_number):
        """
        Retrieve radios associated with an AP.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/aps/{serial_number}/radios`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.

        Returns:
            (dict): API response with radio details for the AP.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        return execute_get(central_conn, endpoint=f"{MONITOR_TYPE}/{serial_number}/radios")

    @staticmethod
    def get_ap_radio_trends(
        central_conn,
        serial_number,
        radio_number,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve trend data for a radio under an AP.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/throughput-trends`
        `GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/channel-utilization-trends`
        `GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/channel-quality-trends`
        `GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/noise-floor-trends`
        `GET network-monitoring/v1/aps/{serial_number}/radios/{radio_number}/frames-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.
            radio_number (str|int): Radio number under the AP.
            metric (str): Radio trend metric to retrieve.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string or seconds for relative queries.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, radio_number, or metric is invalid.
        """
        validate_required_value("radio_number", radio_number)
        return MonitoringAPs._execute_trend_request(
            central_conn=central_conn,
            serial_number=serial_number,
            metric=metric,
            metric_map=RADIO_TREND_METRICS,
            resource_path=f"radios/{radio_number}",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_ap_ports(central_conn, serial_number):
        """
        Retrieve ports associated with an AP.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/aps/{serial_number}/ports`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.

        Returns:
            (dict): API response with port details for the AP.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        return execute_get(central_conn, endpoint=f"{MONITOR_TYPE}/{serial_number}/ports")

    @staticmethod
    def get_ap_port_trends(
        central_conn,
        serial_number,
        port_index,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve trend data for a port under an AP.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/throughput-trends`
        `GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/frames-trends`
        `GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/crc-trends`
        `GET network-monitoring/v1/aps/{serial_number}/ports/{port_index}/collisions-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.
            port_index (str|int): Port index under the AP.
            metric (str): Port trend metric to retrieve.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string or seconds for relative queries.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, port_index, or metric is invalid.
        """
        validate_required_value("port_index", port_index)
        return MonitoringAPs._execute_trend_request(
            central_conn=central_conn,
            serial_number=serial_number,
            metric=metric,
            metric_map=PORT_TREND_METRICS,
            resource_path=f"ports/{port_index}",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_all_ap_tunnels(
        central_conn,
        serial_number,
        site_id=None,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all AP tunnels, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/aps/{serial_number}/tunnels`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.
            site_id (str, optional): Site identifier for the tunnel list.
            filter_str (str, optional): Optional filter expression for the tunnel list.
            sort (str, optional): Optional sort expression for the tunnel list.

        Returns:
            (list[dict]): List of tunnel items for the AP.
        """
        return get_all_pages(
            MonitoringAPs.get_ap_tunnels,
            limit=TUNNEL_LIMIT,
            central_conn=central_conn,
            serial_number=serial_number,
            site_id=site_id,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_ap_tunnels(
        central_conn,
        serial_number,
        site_id=None,
        filter_str=None,
        sort=None,
        limit=TUNNEL_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of AP tunnels.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/aps/{serial_number}/tunnels`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.
            site_id (str, optional): Site identifier for the tunnel list.
            filter_str (str, optional): Optional filter expression for the tunnel list.
            sort (str, optional): Optional sort expression for the tunnel list.
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for the next page.

        Returns:
            (dict): API response for the AP tunnels endpoint.

        Raises:
            ParameterError: If serial_number, limit, next_page, site_id, filter_str, or sort is invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_limit_and_next(limit, next_page, TUNNEL_LIMIT)
        validate_site_id(site_id)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/tunnels",
            params={
                "site-id": site_id,
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_ap_tunnel_details(central_conn, serial_number, tunnel_id):
        """
        Retrieve details for a tunnel under an AP.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.
            tunnel_id (str): Tunnel identifier under the AP.

        Returns:
            (dict): API response with tunnel details.

        Raises:
            ParameterError: If serial_number or tunnel_id is invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("tunnel_id", tunnel_id)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/tunnels/{tunnel_id}",
        )

    @staticmethod
    def get_ap_tunnel_trends(
        central_conn,
        serial_number,
        tunnel_id,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve trend data for a tunnel under an AP.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/throughput-trends`
        `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/packet-loss-trends`
        `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/mos-trends`
        `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/jitter-trends`
        `GET network-monitoring/v1/aps/{serial_number}/tunnels/{tunnel_id}/latency-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.
            tunnel_id (str): Tunnel identifier under the AP.
            metric (str): Tunnel trend metric to retrieve.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string or seconds for relative queries.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, tunnel_id, or metric is invalid.
        """
        validate_required_value("tunnel_id", tunnel_id)
        return MonitoringAPs._execute_trend_request(
            central_conn=central_conn,
            serial_number=serial_number,
            metric=metric,
            metric_map=TUNNEL_TREND_METRICS,
            resource_path=f"tunnels/{tunnel_id}",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_ap_wlans(central_conn, serial_number):
        """
        Retrieve WLANs associated with an AP.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/aps/{serial_number}/wlans`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the AP.

        Returns:
            (dict): API response of associated WLANs.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        return execute_get(central_conn, endpoint=f"{MONITOR_TYPE}/{serial_number}/wlans")
