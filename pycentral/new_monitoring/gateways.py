from ..exceptions import ParameterError
from ..utils.monitoring_utils import (
    build_trend_params,
    clean_raw_trend_data,
    execute_get,
    get_all_pages,
    merged_dict_to_sorted_list,
    normalize_metric,
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
        """Retrieve all gateways, handling pagination."""
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
        """Retrieve a single page of gateways."""
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
        """Get details for a specific gateway."""
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
        """Retrieve all gateway ports, handling pagination."""
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
        """Retrieve a single page of gateway ports."""
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
        """Get details for a specific gateway port."""
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
        """Retrieve all gateway VLANs, handling pagination."""
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
        """Retrieve a single page of gateway VLANs."""
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
        """Get details for a specific gateway VLAN."""
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
        """Retrieve all gateway tunnels, handling pagination."""
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
        """Retrieve a single page of gateway tunnels."""
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
        """Get details for a specific gateway tunnel."""
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("tunnel_name", tunnel_name)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/tunnels/{tunnel_name}"
        )

    @staticmethod
    def get_gateway_uplinks(central_conn, serial_number, sort=None):
        """Retrieve gateway uplinks."""
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_query_length("sort", sort)
        return execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/uplinks",
            params={"sort": sort}
        )

    @staticmethod
    def get_gateway_uplink_details(central_conn, serial_number, link_tag):
        """Get details for a specific gateway uplink."""
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
        """Retrieve all gateway DHCP pools, handling pagination."""
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
        """Retrieve a single page of gateway DHCP pools."""
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
        """Retrieve all gateway DHCP clients, handling pagination."""
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
        """Retrieve a single page of gateway DHCP clients."""
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
        """Retrieve trend data for a gateway metric."""
        validate_central_conn_and_serial(central_conn, serial_number)
        metric = normalize_metric(metric, GATEWAY_TREND_METRICS)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        response = execute_get(
            central_conn,
            endpoint=f"{MONITOR_TYPE}/{serial_number}/{GATEWAY_TREND_METRICS[metric]}",
            params=params,
        )
        return normalize_trend_response(response, return_raw_response)

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
        """Retrieve CPU utilization trends for a gateway."""
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
        """Retrieve memory utilization trends for a gateway."""
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
        """Retrieve WAN availability trends for a gateway."""
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
        """Retrieve VPN availability trends for a gateway."""
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
        """Retrieve hardware temperature trends for a gateway."""
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
        """Collect CPU, memory, and WAN availability trends for a gateway."""
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
        """Get the latest gateway statistics."""
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
        """Retrieve trend data for a gateway port metric."""
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("port_number", port_number)
        metric = normalize_metric(metric, PORT_TREND_METRICS)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        response = execute_get(
            central_conn,
            endpoint=(
                f"{MONITOR_TYPE}/{serial_number}/ports/{port_number}/"
                f"{PORT_TREND_METRICS[metric]}"
            ),
            params=params,
        )
        return normalize_trend_response(response, return_raw_response)

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
        """Retrieve trend data for a gateway tunnel metric."""
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("tunnel_name", tunnel_name)
        metric = normalize_metric(metric, TUNNEL_TREND_METRICS)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        response = execute_get(
            central_conn,
            endpoint=(
                f"{MONITOR_TYPE}/{serial_number}/tunnels/{tunnel_name}/"
                f"{TUNNEL_TREND_METRICS[metric]}"
            ),
            params=params
        )
        return normalize_trend_response(response, return_raw_response)

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
        """Retrieve trend data for a gateway uplink metric."""
        validate_central_conn_and_serial(central_conn, serial_number)
        validate_required_value("link_tag", link_tag)
        metric = normalize_metric(metric, UPLINK_TREND_METRICS)
        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        response = execute_get(
            central_conn,
            endpoint=(
                f"{MONITOR_TYPE}/{serial_number}/uplinks/{link_tag}/"
                f"{UPLINK_TREND_METRICS[metric]}"
            ),
            params=params
        )
        return normalize_trend_response(response, return_raw_response)

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
        """Retrieve uplink VPN availability trends using VLAN identifier."""
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
        """Retrieve probe definitions for a gateway uplink."""
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
        """Retrieve performance trends for a gateway uplink probe."""
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
        """Retrieve tunnel health summary for a gateway."""
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
        """Retrieve all cluster members, handling pagination."""
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
        """Retrieve a single page of cluster members."""
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
        """Retrieve all cluster tunnels, handling pagination."""
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
        """Retrieve a single page of cluster tunnels."""
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
        """Retrieve VLAN mismatch details for a cluster."""
        validate_required_value("cluster_name", cluster_name)
        validate_query_length("filter_str", filter_str)
        return execute_get(
            central_conn,
            endpoint=f"{CLUSTER_MONITOR_TYPE}/{cluster_name}/vlan-mismatch",
            params={"filter": filter_str}
        )

    @staticmethod
    def get_cluster_connectivity_graph(central_conn, cluster_name):
        """Retrieve connectivity graph details for a cluster."""
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
        """Retrieve cluster tunnel health or status summary."""
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
        """Retrieve cluster capacity trends."""
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
