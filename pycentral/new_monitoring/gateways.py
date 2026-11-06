from ..exceptions import ParameterError
from ..utils.monitoring_utils import (
    build_trend_params,
    clean_raw_trend_data,
    execute_get,
    execute_trend_request,
    get_all_pages,
    merged_dict_to_sorted_list,
    normalize_trend_response,
    validate_central_conn_and_serial,
    validate_limit_and_next,
    validate_query_length,
    validate_required_value,
    validate_site_id,
)
from .constants import (
    CLUSTER_LIMIT,
    GATEWAY_DHCP_LIMIT,
    GATEWAY_LIMIT,
    GATEWAY_VLAN_LIMIT,
)

MONITOR_TYPE = "gateways"
CLUSTER_MONITOR_TYPE = "clusters"

GATEWAY_TREND_METRICS = {
    "cpu-utilization": "cpu-utilization-trends",
    "memory-utilization": "memory-utilization-trends",
    "wan-availability": "wan-availability-trends",
    "vpn-availability": "vpn-availability-trends",
    "hardware-temperature": "hardware-temperature-trends",
}
PORT_TREND_METRICS = {
    "throughput": "throughput-trends",
    "frames": "frames-trends",
    "frames-errors": "frames-errors-trends",
    "frames-packets": "frames-packets-trends",
}
TUNNEL_TREND_METRICS = {
    "throughput": "throughput-trends",
    "status": "status-trends",
    "dropped-packets": "dropped-packet-trends",
}
UPLINK_TREND_METRICS = {
    "throughput": "throughput-trends",
    "wan-compression": "wan-compression-trends",
    "wan-availability": "wan-availability-trends",
}


class MonitoringGateways:
    @staticmethod
    def get_all_gateways(central_conn, filter_str=None, sort=None):
        """
        Retrieve all gateways, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/gateways`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of gateway items.
        """
        return get_all_pages(
            MonitoringGateways.get_gateways,
            limit=GATEWAY_LIMIT,
            central_conn=central_conn,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_gateways(
        central_conn,
        filter_str=None,
        sort=None,
        limit=GATEWAY_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of gateways.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/gateways`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the gateways endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If limit or next_page values are invalid.
        """
        validate_limit_and_next(limit, next_page, GATEWAY_LIMIT)
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
    def get_gateway_details(central_conn, serial_number):
        """
        Get details for a specific gateway.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/gateways/{serial_number}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.

        Returns:
            (dict): API response with gateway details.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}",
        )

    @staticmethod
    def get_all_gateway_ports(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all gateway ports, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/ports`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of gateway port items.
        """
        return get_all_pages(
            MonitoringGateways.get_gateway_ports,
            limit=GATEWAY_LIMIT,
            central_conn=central_conn,
            serial_number=serial_number,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_gateway_ports(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
        limit=GATEWAY_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of gateway ports.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/ports`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the gateway ports endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If serial_number, limit, or next_page values are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_limit_and_next(limit, next_page, GATEWAY_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/ports",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_gateway_port_details(central_conn, serial_number, port_number):
        """
        Get details for a specific gateway port.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            port_number (str): Port number identifier.

        Returns:
            (dict): API response with gateway port details.

        Raises:
            ParameterError: If serial_number or port_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("port_number", port_number)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/ports/{port_number}",
        )

    @staticmethod
    def get_all_gateway_vlans(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all gateway VLANs, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/vlans`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of gateway VLAN items.
        """
        return get_all_pages(
            MonitoringGateways.get_gateway_vlans,
            limit=GATEWAY_VLAN_LIMIT,
            central_conn=central_conn,
            serial_number=serial_number,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_gateway_vlans(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
        limit=GATEWAY_VLAN_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of gateway VLANs.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/vlans`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the gateway VLANs endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If serial_number, limit, or next_page values are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_limit_and_next(limit, next_page, GATEWAY_VLAN_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/vlans",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_gateway_vlan_details(central_conn, serial_number, vlan_id):
        """
        Get details for a specific gateway VLAN.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/vlans/{vlan_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            vlan_id (str): VLAN identifier.

        Returns:
            (dict): API response with gateway VLAN details.

        Raises:
            ParameterError: If serial_number or vlan_id is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("vlan_id", vlan_id)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/vlans/{vlan_id}",
        )

    @staticmethod
    def get_all_gateway_tunnels(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all gateway tunnels, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of gateway tunnel items.
        """
        return get_all_pages(
            MonitoringGateways.get_gateway_tunnels,
            limit=GATEWAY_LIMIT,
            central_conn=central_conn,
            serial_number=serial_number,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_gateway_tunnels(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
        limit=GATEWAY_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of gateway tunnels.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the gateway tunnels endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If serial_number, limit, or next_page values are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_limit_and_next(limit, next_page, GATEWAY_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/tunnels",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            },
        )

    @staticmethod
    def get_gateway_tunnel_details(central_conn, serial_number, tunnel_name):
        """
        Get details for a specific gateway tunnel.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            tunnel_name (str): Name of the tunnel.

        Returns:
            (dict): API response with gateway tunnel details.

        Raises:
            ParameterError: If serial_number or tunnel_name is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("tunnel_name", tunnel_name)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/tunnels/{tunnel_name}"
        )

    @staticmethod
    def get_gateway_uplinks(central_conn, serial_number, sort=None):
        """
        Retrieve all uplinks for a gateway.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (dict): API response with uplink records for the gateway.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_query_length("sort", sort)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/uplinks",
            params={"sort": sort}
        )

    @staticmethod
    def get_gateway_uplink_details(central_conn, serial_number, link_tag):
        """
        Get details for a specific gateway uplink.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            link_tag (str): Uplink link tag identifier.

        Returns:
            (dict): API response with gateway uplink details.

        Raises:
            ParameterError: If serial_number or link_tag is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("link_tag", link_tag)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/uplinks/{link_tag}"
        )

    @staticmethod
    def get_all_gateway_dhcp_pools(
        central_conn,
        serial_number,
        sort=None,
    ):
        """
        Retrieve all gateway DHCP pools, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/dhcp-pools`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of gateway DHCP pool items.
        """
        return get_all_pages(
            MonitoringGateways.get_gateway_dhcp_pools,
            limit=GATEWAY_DHCP_LIMIT,
            central_conn=central_conn,
            serial_number=serial_number,
            sort=sort,
        )

    @staticmethod
    def get_gateway_dhcp_pools(
        central_conn,
        serial_number,
        sort=None,
        limit=GATEWAY_DHCP_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of gateway DHCP pools.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/dhcp-pools`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the gateway DHCP pools endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If serial_number, limit, or next_page values are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_limit_and_next(limit, next_page, GATEWAY_DHCP_LIMIT)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/dhcp-pools",
            params={
                "sort": sort,
                "limit": limit,
                "next": next_page,
            }
        )

    @staticmethod
    def get_all_gateway_dhcp_clients(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all gateway DHCP clients, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/dhcp-clients`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of gateway DHCP client items.
        """
        return get_all_pages(
            MonitoringGateways.get_gateway_dhcp_clients,
            limit=GATEWAY_DHCP_LIMIT,
            central_conn=central_conn,
            serial_number=serial_number,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_gateway_dhcp_clients(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
        limit=GATEWAY_DHCP_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of gateway DHCP clients.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/dhcp-clients`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the gateway DHCP clients endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If serial_number, limit, or next_page values are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_limit_and_next(limit, next_page, GATEWAY_DHCP_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/dhcp-clients",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            }
        )

    @staticmethod
    def get_gateway_trends(
        central_conn,
        serial_number,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve trend data for a gateway metric.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/gateways/{serial_number}/cpu-utilization-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/memory-utilization-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/wan-availability-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/vpn-availability-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/hardware-temperature-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            metric (str): Trend metric to retrieve. Supported values are `cpu-utilization`, `memory-utilization`, `wan-availability`, `vpn-availability`, and `hardware-temperature`.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number or metric is invalid.
        """
        return execute_trend_request(
            central_conn=central_conn,
            base_path=MONITOR_TYPE,
            serial_number=serial_number,
            metric=metric,
            metric_map=GATEWAY_TREND_METRICS,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_cpu_utilization(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve CPU utilization trends for a gateway.

        Shortcut for `get_gateway_trends(..., metric="cpu-utilization")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/cpu-utilization-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_trends(
            central_conn,
            serial_number,
            metric="cpu-utilization",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_memory_utilization(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve memory utilization trends for a gateway.

        Shortcut for `get_gateway_trends(..., metric="memory-utilization")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/memory-utilization-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_trends(
            central_conn,
            serial_number,
            metric="memory-utilization",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_wan_availability(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve WAN availability trends for a gateway.

        Shortcut for `get_gateway_trends(..., metric="wan-availability")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/wan-availability-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_trends(
            central_conn,
            serial_number,
            metric="wan-availability",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_vpn_availability(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve VPN availability trends for a gateway.

        Shortcut for `get_gateway_trends(..., metric="vpn-availability")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/vpn-availability-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_trends(
            central_conn,
            serial_number,
            metric="vpn-availability",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_temperature_trends(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve hardware temperature trends for a gateway.

        Shortcut for `get_gateway_trends(..., metric="hardware-temperature")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/hardware-temperature-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_trends(
            central_conn,
            serial_number,
            metric="hardware-temperature",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_stats(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Collect CPU, memory and WAN availability trends for a gateway, merged by timestamp.

        Makes three calls, the same as `get_gateway_trends` with `metric` set to
        `cpu-utilization`, `memory-utilization` and `wan-availability`:
        `GET network-monitoring/v1/gateways/{serial_number}/cpu-utilization-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/memory-utilization-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/wan-availability-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the three raw API responses. Otherwise merge them into one list sorted by timestamp.

        Returns:
            (list): The three raw responses if return_raw_response is True; otherwise samples sorted by timestamp, one key per metric.

        Raises:
            ParameterError: If serial_number or the time arguments are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)

        raw_results = []
        for metric in (
            "cpu-utilization",
            "memory-utilization",
            "wan-availability",
        ):
            raw_results.append(
                MonitoringGateways.get_gateway_trends(
                    central_conn,
                    serial_number,
                    metric=metric,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    site_id=site_id,
                    return_raw_response=True,
                )
            )

        if return_raw_response:
            return raw_results

        data = {}
        for response in raw_results:
            if isinstance(response, dict):
                data = clean_raw_trend_data(response, data=data)
        return merged_dict_to_sorted_list(data)

    @staticmethod
    def get_latest_gateway_stats(central_conn, serial_number):
        """
        Get the most recent CPU, memory and WAN availability sample for a gateway.

        Calls `get_gateway_stats(..., duration="5m")` and returns its last sample.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.

        Returns:
            (dict): The latest sample, or an empty dict if none was returned.

        Raises:
            ParameterError: If serial_number is invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        stats = MonitoringGateways.get_gateway_stats(
            central_conn,
            serial_number,
            duration="5m",
        )
        return stats[-1] if isinstance(stats, list) and stats else {}

    @staticmethod
    def get_gateway_port_trends(
        central_conn,
        serial_number,
        port_number,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve trend data for a gateway port metric.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/throughput-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-errors-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-packets-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            port_number (str): Port number identifier.
            metric (str): Port trend metric to retrieve. Supported values are `throughput`, `frames`, `frames-errors`, and `frames-packets`.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If port_number or metric is invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("port_number", port_number)
        return execute_trend_request(
            central_conn=central_conn,
            base_path=MONITOR_TYPE,
            serial_number=serial_number,
            metric=metric,
            metric_map=PORT_TREND_METRICS,
            resource_path=f"ports/{port_number}",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_port_throughput_trends(
        central_conn,
        serial_number,
        port_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve port throughput trends for a gateway.

        Shortcut for `get_gateway_port_trends(..., metric="throughput")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/throughput-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            port_number (str): Port number on the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, port_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_port_trends(
            central_conn,
            serial_number,
            port_number,
            metric="throughput",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_port_frames_trends(
        central_conn,
        serial_number,
        port_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve port frame trends for a gateway.

        Shortcut for `get_gateway_port_trends(..., metric="frames")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            port_number (str): Port number on the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, port_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_port_trends(
            central_conn,
            serial_number,
            port_number,
            metric="frames",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_port_frames_errors_trends(
        central_conn,
        serial_number,
        port_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve port frame-error trends for a gateway.

        Shortcut for `get_gateway_port_trends(..., metric="frames-errors")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-errors-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            port_number (str): Port number on the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, port_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_port_trends(
            central_conn,
            serial_number,
            port_number,
            metric="frames-errors",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_port_frames_packets_trends(
        central_conn,
        serial_number,
        port_number,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve port frame-packet trends for a gateway.

        Shortcut for `get_gateway_port_trends(..., metric="frames-packets")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/ports/{port_number}/frames-packets-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            port_number (str): Port number on the gateway.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, port_number or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_port_trends(
            central_conn,
            serial_number,
            port_number,
            metric="frames-packets",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_tunnel_trends(
        central_conn,
        serial_number,
        tunnel_name,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve trend data for a gateway tunnel metric.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/throughput-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/status-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/dropped-packet-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            tunnel_name (str): Name of the tunnel.
            metric (str): Tunnel trend metric to retrieve. Supported values are `throughput`, `status`, and `dropped-packets`.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If tunnel_name or metric is invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("tunnel_name", tunnel_name)
        return execute_trend_request(
            central_conn=central_conn,
            base_path=MONITOR_TYPE,
            serial_number=serial_number,
            metric=metric,
            metric_map=TUNNEL_TREND_METRICS,
            resource_path=f"tunnels/{tunnel_name}",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_tunnel_throughput_trends(
        central_conn,
        serial_number,
        tunnel_name,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve tunnel throughput trends for a gateway.

        Shortcut for `get_gateway_tunnel_trends(..., metric="throughput")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/throughput-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            tunnel_name (str): Name of the tunnel.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, tunnel_name or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_tunnel_trends(
            central_conn,
            serial_number,
            tunnel_name,
            metric="throughput",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_tunnel_status_trends(
        central_conn,
        serial_number,
        tunnel_name,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve tunnel status trends for a gateway.

        Shortcut for `get_gateway_tunnel_trends(..., metric="status")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/status-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            tunnel_name (str): Name of the tunnel.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, tunnel_name or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_tunnel_trends(
            central_conn,
            serial_number,
            tunnel_name,
            metric="status",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_tunnel_dropped_packets_trends(
        central_conn,
        serial_number,
        tunnel_name,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve tunnel dropped-packet trends for a gateway.

        Shortcut for `get_gateway_tunnel_trends(..., metric="dropped-packets")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/tunnels/{tunnel_name}/dropped-packet-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            tunnel_name (str): Name of the tunnel.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, tunnel_name or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_tunnel_trends(
            central_conn,
            serial_number,
            tunnel_name,
            metric="dropped-packets",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_uplink_trends(
        central_conn,
        serial_number,
        link_tag,
        metric,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve trend data for a gateway uplink metric.

        This method makes an API call to one of the following endpoints based on `metric` -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/throughput-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-compression-trends`
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-availability-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            link_tag (str): Uplink link tag identifier.
            metric (str): Uplink trend metric to retrieve. Supported values are `throughput`, `wan-compression`, and `wan-availability`.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If link_tag or metric is invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("link_tag", link_tag)
        return execute_trend_request(
            central_conn=central_conn,
            base_path=MONITOR_TYPE,
            serial_number=serial_number,
            metric=metric,
            metric_map=UPLINK_TREND_METRICS,
            resource_path=f"uplinks/{link_tag}",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_uplink_throughput_trends(
        central_conn,
        serial_number,
        link_tag,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve uplink throughput trends for a gateway.

        Shortcut for `get_gateway_uplink_trends(..., metric="throughput")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/throughput-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            link_tag (str): Uplink link tag.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, link_tag or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_uplink_trends(
            central_conn,
            serial_number,
            link_tag,
            metric="throughput",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_uplink_wan_compression_trends(
        central_conn,
        serial_number,
        link_tag,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve uplink WAN compression trends for a gateway.

        Shortcut for `get_gateway_uplink_trends(..., metric="wan-compression")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-compression-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            link_tag (str): Uplink link tag.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, link_tag or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_uplink_trends(
            central_conn,
            serial_number,
            link_tag,
            metric="wan-compression",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_uplink_wan_availability_trends(
        central_conn,
        serial_number,
        link_tag,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve uplink WAN availability trends for a gateway.

        Shortcut for `get_gateway_uplink_trends(..., metric="wan-availability")`; sends the same request.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/wan-availability-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            link_tag (str): Uplink link tag.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, link_tag or the time arguments are invalid.
        """
        return MonitoringGateways.get_gateway_uplink_trends(
            central_conn,
            serial_number,
            link_tag,
            metric="wan-availability",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
            return_raw_response=return_raw_response,
        )

    @staticmethod
    def get_gateway_uplink_vpn_availability_trends(
        central_conn,
        serial_number,
        vlan_id,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve VPN availability trends for a gateway uplink using a VLAN identifier.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{vlan_id}/vpn-availability-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            vlan_id (str): VLAN identifier for the uplink.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number or vlan_id is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("vlan_id", vlan_id)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        response = execute_get(
            central_conn,
            endpoint=(
                f"{MONITOR_TYPE}/{serial_number}/uplinks/{vlan_id}/"
                "vpn-availability-trends"
            ),
            params=params
        )
        return normalize_trend_response(response, return_raw_response)

    @staticmethod
    def get_gateway_uplink_probes(
        central_conn,
        serial_number,
        link_tag,
        filter_str=None,
        site_id=None,
    ):
        """
        Retrieve probe definitions for a specific gateway uplink.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/probes`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            link_tag (str): Uplink link tag identifier.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            site_id (str, optional): Site identifier to scope the request.

        Returns:
            (dict): API response with probe definitions for the uplink.

        Raises:
            ParameterError: If serial_number or link_tag is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("link_tag", link_tag)
        validate_query_length("filter_str", filter_str)
        validate_site_id(site_id)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/uplinks/{link_tag}/probes",
            params={
                "filter": filter_str,
                "site-id": site_id,
            }
        )

    @staticmethod
    def get_gateway_uplink_probe_performance_trends(
        central_conn,
        serial_number,
        link_tag,
        probe,
        start_time=None,
        end_time=None,
        duration=None,
        site_id=None,
        return_raw_response=False,
    ):
        """
        Retrieve performance trends for a specific gateway uplink probe.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/gateways/{serial_number}/uplinks/{link_tag}/probes/{probe}/performance-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            link_tag (str): Uplink link tag identifier.
            probe (str): Probe identifier.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            site_id (str, optional): Site identifier to scope the trend request.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If serial_number, link_tag, or probe is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("link_tag", link_tag)
        validate_required_value("probe", probe)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        response = execute_get(
            central_conn,
            endpoint=(
                f"{MONITOR_TYPE}/{serial_number}/uplinks/{link_tag}/probes/{probe}/"
                "performance-trends"
            ),
            params=params
        )
        return normalize_trend_response(response, return_raw_response)

    @staticmethod
    def get_gateway_tunnel_health_summary(
        central_conn,
        serial_number,
        tunnel_type="lan",
    ):
        """
        Retrieve LAN or WAN tunnel health summary for a gateway.

        This method makes an API call to one of the following endpoints based on `tunnel_type` -
        `GET network-monitoring/v1/gateways/{serial_number}/lan-tunnels-health-summary`
        `GET network-monitoring/v1/gateways/{serial_number}/wan-tunnels-health-summary`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the gateway.
            tunnel_type (str, optional): Type of tunnel health summary. Supported values are `lan` and `wan` (default is `lan`).

        Returns:
            (dict): API response with tunnel health summary data.

        Raises:
            ParameterError: If serial_number is missing/invalid or tunnel_type is not `lan` or `wan`.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        normalized_tunnel_type = str(tunnel_type).lower()
        tunnel_paths = {
            "lan": "lan-tunnels-health-summary",
            "wan": "wan-tunnels-health-summary",
        }
        if normalized_tunnel_type not in tunnel_paths:
            raise ParameterError("tunnel_type must be either 'lan' or 'wan'")
        return execute_get(
            central_conn,
            endpoint=(
                f"{MONITOR_TYPE}/{serial_number}/"
                f"{tunnel_paths[normalized_tunnel_type]}"
            )
        )

    @staticmethod
    def get_all_cluster_members(
        central_conn,
        cluster_name,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all cluster members, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/clusters/{cluster_name}/members`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of cluster member items.

        Raises:
            ParameterError: If cluster_name is missing/invalid.
        """
        validate_required_value("cluster_name", cluster_name)
        return get_all_pages(
            MonitoringGateways.get_cluster_members,
            limit=CLUSTER_LIMIT,
            central_conn=central_conn,
            cluster_name=cluster_name,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_cluster_members(
        central_conn,
        cluster_name,
        filter_str=None,
        sort=None,
        limit=CLUSTER_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of cluster members.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/clusters/{cluster_name}/members`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the cluster members endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If cluster_name, limit, or next_page values are invalid.
        """
        validate_required_value("cluster_name", cluster_name)
        validate_limit_and_next(limit, next_page, CLUSTER_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)
        return execute_get(
            central_conn,
            endpoint=f"{CLUSTER_MONITOR_TYPE}/{cluster_name}/members",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            }
        )

    @staticmethod
    def get_all_cluster_tunnels(
        central_conn,
        cluster_name,
        filter_str=None,
        sort=None,
    ):
        """
        Retrieve all cluster tunnels, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/clusters/{cluster_name}/tunnels`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of cluster tunnel items.

        Raises:
            ParameterError: If cluster_name is missing/invalid.
        """
        validate_required_value("cluster_name", cluster_name)
        return get_all_pages(
            MonitoringGateways.get_cluster_tunnels,
            limit=CLUSTER_LIMIT,
            central_conn=central_conn,
            cluster_name=cluster_name,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_cluster_tunnels(
        central_conn,
        cluster_name,
        filter_str=None,
        sort=None,
        limit=CLUSTER_LIMIT,
        next_page=1,
    ):
        """
        Retrieve a single page of cluster tunnels.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/clusters/{cluster_name}/tunnels`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return.
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the cluster tunnels endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If cluster_name, limit, or next_page values are invalid.
        """
        validate_required_value("cluster_name", cluster_name)
        validate_limit_and_next(limit, next_page, CLUSTER_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)
        return execute_get(
            central_conn,
            endpoint=f"{CLUSTER_MONITOR_TYPE}/{cluster_name}/tunnels",
            params={
                "filter": filter_str,
                "sort": sort,
                "limit": limit,
                "next": next_page,
            }
        )

    @staticmethod
    def get_cluster_vlan_mismatch(
        central_conn,
        cluster_name,
        filter_str=None,
    ):
        """
        Retrieve VLAN mismatch details for a cluster.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/clusters/{cluster_name}/vlan-mismatch`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).

        Returns:
            (dict): API response with VLAN mismatch details.

        Raises:
            ParameterError: If cluster_name is missing/invalid.
        """
        validate_required_value("cluster_name", cluster_name)
        validate_query_length("filter_str", filter_str)
        return execute_get(
            central_conn,
            endpoint=f"{CLUSTER_MONITOR_TYPE}/{cluster_name}/vlan-mismatch",
            params={"filter": filter_str}
        )

    @staticmethod
    def get_cluster_connectivity_graph(central_conn, cluster_name):
        """
        Retrieve connectivity graph details for a cluster.

        This method makes an API call to the following endpoint -
        `GET network-monitoring/v1/clusters/{cluster_name}/connectivity-graph`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.

        Returns:
            (dict): API response with cluster connectivity graph details.

        Raises:
            ParameterError: If cluster_name is missing/invalid.
        """
        validate_required_value("cluster_name", cluster_name)
        return execute_get(
            central_conn,
            endpoint=f"{CLUSTER_MONITOR_TYPE}/{cluster_name}/connectivity-graph"
        )

    @staticmethod
    def get_cluster_tunnel_summary(
        central_conn,
        cluster_name,
        summary_type="health",
    ):
        """
        Retrieve cluster tunnel health or status summary.

        This method makes an API call to one of the following endpoints based on `summary_type` -
        `GET network-monitoring/v1/clusters/{cluster_name}/tunnels-health-summary`
        `GET network-monitoring/v1/clusters/{cluster_name}/tunnels-status-summary`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.
            summary_type (str, optional): Type of tunnel summary. Supported values are `health` and `status` (default is `health`).

        Returns:
            (dict): API response with cluster tunnel health or status summary.

        Raises:
            ParameterError: If cluster_name is missing/invalid or summary_type is not `health` or `status`.
        """
        validate_required_value("cluster_name", cluster_name)
        normalized_summary_type = str(summary_type).lower()
        summary_paths = {
            "health": "tunnels-health-summary",
            "status": "tunnels-status-summary",
        }
        if normalized_summary_type not in summary_paths:
            raise ParameterError("summary_type must be either 'health' or 'status'")
        return execute_get(
            central_conn,
            endpoint=(
                f"{CLUSTER_MONITOR_TYPE}/{cluster_name}/"
                f"{summary_paths[normalized_summary_type]}"
            )
        )

    @staticmethod
    def get_cluster_capacity_trends(
        central_conn,
        cluster_name,
        serial_number=None,
        start_time=None,
        end_time=None,
        duration=None,
        return_raw_response=False,
    ):
        """
        Retrieve cluster capacity trends, optionally scoped to a specific cluster member.

        This method makes an API call to one of the following endpoints -
        `GET network-monitoring/v1/clusters/{cluster_name}/capacity-trends`
        `GET network-monitoring/v1/clusters/{cluster_name}/capacity-trends/{serial_number}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            cluster_name (str): Name of the cluster.
            serial_number (str, optional): Serial number of a specific cluster member. If provided, scopes the trends to that member.
            start_time (str|int, optional): Start of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires end_time.
            end_time (str|int, optional): End of the time window: RFC3339 string or Unix epoch (seconds or milliseconds). Requires start_time.
            duration (str, optional): Window ending now, e.g. '30m', '3h', '2d', '1w' (minutes, hours, days, weeks; max 90 days). Cannot be combined with start_time/end_time.
            return_raw_response (bool, optional): If True, return the raw API payload. Otherwise return normalized trend samples.

        Returns:
            (dict|list): If return_raw_response is True returns the raw API response; otherwise returns normalized trend samples.

        Raises:
            ParameterError: If cluster_name is missing/invalid.
        """
        validate_required_value("cluster_name", cluster_name)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
        )
        endpoint = f"{CLUSTER_MONITOR_TYPE}/{cluster_name}/capacity-trends"
        if serial_number is not None:
            validate_required_value("serial_number", serial_number)
            endpoint = f"{endpoint}/{serial_number}"
        response = execute_get(
            central_conn,
            endpoint=endpoint,
            params=params
        )
        return normalize_trend_response(response, return_raw_response)
