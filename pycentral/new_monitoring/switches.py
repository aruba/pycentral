from ..utils.monitoring_utils import (
    build_trend_params,
    execute_get,
    get_all_pages,
    normalize_trend_response,
    validate_central_conn_and_serial,
    validate_limit_and_next,
    validate_query_length,
)
from ..exceptions import ParameterError
from .constants import SWITCH_LIMIT

MONITOR_TYPE = "switches"


class MonitoringSwitches:
    @staticmethod
    def get_all_switches(central_conn, filter_str=None, sort=None):
        """
        Retrieve all switches, handling pagination.

        This method retrieves all results by repeatedly calling the following endpoint -
        `GET network-monitoring/v1/switches`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
                See get_switches() for supported fields and operators.
            sort (str, optional): Optional sort parameter. See get_switches() for supported fields.

        Returns:
            (list[dict]): List of switch items.
        """
        return get_all_pages(
            MonitoringSwitches.get_switches,
            limit=SWITCH_LIMIT,
            central_conn=central_conn,
            filter_str=filter_str,
            sort=sort,
        )

    @staticmethod
    def get_switches(
        central_conn, filter_str=None, sort=None, limit=SWITCH_LIMIT, next_page=1
    ):
        """
        Retrieve a single page of switches associated to a customer, based on the query parameters provided.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData Version 4.0 filter string (limited functionality). Supports only
                'and' conjunction ('or' and 'not' are NOT supported). Max length 256.
                Supported fields and operators:
                - siteId (eq, in), siteName (eq, in), model (eq, in), status (eq, in), deployment (eq, in).
            sort (str, optional): Comma separated list of sort expressions. Each expression is a field name
                optionally followed by 'asc' or 'desc'. Max length 256.
                Supported fields: siteId, model, status, deployment, serialNumber, deviceName.
            limit (int, optional): Maximum number of switches to return (0-1000, default is 1000).
            next_page (int, optional): Pagination cursor for next page of resources (default is 1).

        Returns:
            (dict): API response containing keys like 'items', 'total', and 'next'.

        Raises:
            ParameterError: If limit exceeds 1000 or next_page is less than 1.
            ParameterError: If filter_str exceeds the maximum query length.
            ParameterError: If sort exceeds the maximum query length.
        """
        validate_limit_and_next(limit, next_page, SWITCH_LIMIT)
        validate_query_length("filter_str", filter_str)
        validate_query_length("sort", sort)

        params = {
            "limit": limit,
            "next": next_page,
            "filter": filter_str,
            "sort": sort,
        }

        path = MONITOR_TYPE
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_switch_details(central_conn, serial_number):
        """
        Get details for a specific switch by serial number or stack ID.

        In the case of stacked switches, logical switch details and trend data are also provided.
        The conductor serial may be used instead of a stack ID. Member-level information can be
        obtained using the listStackMember API.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).

        Returns:
            (dict): API response with switch details.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_stack_members(central_conn, serial_number):
        """
        Get stack member details for a given stack ID or conductor serial.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Stack ID or conductor serial number.

        Returns:
            (dict): API response with stack member details.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        path = f"stack/{serial_number}/members"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_switch_hardware_categories(central_conn, serial_number):
        """
        Get hardware details for a specific switch by serial number or stack ID.

        Conductor serial may also be used instead of a stack ID.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).

        Returns:
            (dict): API response with detailed hardware information.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}/hardware-categories"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_switch_lag(central_conn, serial_number):
        """
        Get link aggregation group (LAG) summary details for a specific switch by serial number or stack ID.

        Conductor serial may also be used instead of a stack ID.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).

        Returns:
            (dict): API response with LAG summary details.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}/lag"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_switch_interfaces(
        central_conn,
        serial_number,
        filter_str=None,
        search=None,
        sort=None,
        limit=SWITCH_LIMIT,
        offset=0,
    ):
        """
        Get interface details for a specific switch by serial number or stack ID.

        Conductor serial may also be used instead of a stack ID.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).
            filter_str (str, optional): OData Version 4.0 filter string (limited functionality). Supports only
                'and' conjunction ('or' and 'not' are NOT supported). Max length 256.
                Supported fields and operators:
                - name, speed, status, connector, duplex, lag, vlanmode, neighbourFamily,
                  neighbourFunction, poeClass, poeStatus, operStatus (eq, in).
            search (str, optional): Partial or full string free text search. Max length 256.
            sort (str, optional): Comma separated list of sort expressions. Each expression is a field name
                optionally followed by 'asc' or 'desc'. Max length 256. Default sort by name.
                Supported fields: port, speed, neighbour, neighbourFamily, nativeVlan, neighbourRole,
                alias, connector, lag, vlanMode, poeClass, ipv4, mtu.
            limit (int, optional): Number of interfaces to return (0-1000, default is 1000).
            offset (int, optional): Number of interfaces to skip (default is 0).

        Returns:
            (dict): API response with a list of interfaces.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
            ParameterError: If limit exceeds 1000.
            ParameterError: If filter_str, search, or sort exceed the maximum query length.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        if limit > SWITCH_LIMIT:
            raise ParameterError(f"limit cannot exceed {SWITCH_LIMIT}")
        validate_query_length("filter_str", filter_str)
        validate_query_length("search", search)
        validate_query_length("sort", sort)

        params = {
            "limit": limit,
            "offset": offset,
            "filter": filter_str,
            "search": search,
            "sort": sort,
        }
        path = f"{MONITOR_TYPE}/{serial_number}/interfaces"
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_switch_vlans(
        central_conn,
        serial_number,
        filter_str=None,
        search=None,
        sort=None,
        limit=SWITCH_LIMIT,
        offset=0,
    ):
        """
        Get VLAN details for a specific switch by serial number or stack ID.

        Conductor serial may also be used instead of a stack ID.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).
            filter_str (str, optional): OData Version 4.0 filter string (limited functionality). Supports only
                'and' conjunction ('or' and 'not' are NOT supported). Max length 256.
                Supported fields and operators:
                - status, voice, type (eq, in).
            search (str, optional): Partial or full string free text search. Max length 256.
            sort (str, optional): Comma separated list of sort expressions. Each expression is a field name
                optionally followed by 'asc' or 'desc'. Max length 256. Default sort by id.
                Supported fields: name, id, status, type, ipv4.
            limit (int, optional): Number of VLANs to return (0-1000, default is 1000).
            offset (int, optional): Number of VLANs to skip (default is 0).

        Returns:
            (dict): API response with a list of VLANs.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
            ParameterError: If limit exceeds 1000.
            ParameterError: If filter_str, search, or sort exceed the maximum query length.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        if limit > SWITCH_LIMIT:
            raise ParameterError(f"limit cannot exceed {SWITCH_LIMIT}")
        validate_query_length("filter_str", filter_str)
        validate_query_length("search", search)
        validate_query_length("sort", sort)

        params = {
            "limit": limit,
            "offset": offset,
            "filter": filter_str,
            "search": search,
            "sort": sort,
        }
        path = f"{MONITOR_TYPE}/{serial_number}/vlans"
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_topn_interface_trends(
        central_conn,
        site_id=None,
        start_time=None,
        end_time=None,
        duration=None,
        return_raw_response=False,
    ):
        """
        Get top-N switch interface trends (rx bytes, tx bytes) for a site over a given time period.

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str, optional): ID of the site for which switch-related information is requested.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string (e.g. '3h') or seconds for relative queries.
            return_raw_response (bool, optional): If True, return raw API response; otherwise return
                processed and sorted trend data. Default is False.

        Returns:
            (dict|list): If return_raw_response is True returns raw API response; otherwise returns
                merged, sorted trend statistics.

        Raises:
            ParameterError: If central_conn is None.
            ParameterError: If start_time/end_time/duration arguments are invalid.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")

        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        path = f"{MONITOR_TYPE}/topn-interface-trends"
        response = execute_get(central_conn, endpoint=path, params=params)

        return normalize_trend_response(response, return_raw_response)

    @staticmethod
    def get_switch_interface_trends(
        central_conn,
        serial_number,
        site_id=None,
        interface_id=None,
        uplink=None,
        start_time=None,
        end_time=None,
        duration=None,
        return_raw_response=False,
    ):
        """
        Get interface trend data for a specific switch by serial number or stack ID.

        When a stack ID or conductor serial is provided, trends are aggregated across the entire stack.
        When a member serial is provided, trends are aggregated for that specific member.
        Supported metrics include RX bytes, TX bytes, discards, giants, errors, runts, and collisions.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).
            site_id (str, optional): ID of the site for which switch-related information is requested.
            interface_id (str, optional): Interface name of the switch.
            uplink (bool, optional): Filter by uplink status of the interface.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string (e.g. '3h') or seconds for relative queries.
            return_raw_response (bool, optional): If True, return raw API response; otherwise return
                processed and sorted trend data. Default is False.

        Returns:
            (dict|list): If return_raw_response is True returns raw API response; otherwise returns
                merged, sorted trend data.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
            ParameterError: If start_time/end_time/duration arguments are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)

        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        ) or {}
        params["interface-id"] = interface_id
        params["uplink"] = uplink
        path = f"{MONITOR_TYPE}/{serial_number}/interface-trends"
        response = execute_get(central_conn, endpoint=path, params=params)

        return normalize_trend_response(response, return_raw_response)

    @staticmethod
    def get_switch_hardware_trends(
        central_conn,
        serial_number,
        site_id=None,
        start_time=None,
        end_time=None,
        duration=None,
        return_raw_response=False,
    ):
        """
        Get hardware trend data for a specific switch by serial number or stack ID.

        When a stack ID or conductor serial is provided, trends are aggregated for each member of the stack.
        When a member serial is provided, trends are aggregated for that specific member.
        Available metrics include CPU utilization, memory utilization, PoE available, PoE consumption,
        and total power available. By default, data is aggregated over the last three hours.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).
            site_id (str, optional): ID of the site for which switch-related information is requested.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string (e.g. '3h') or seconds for relative queries.
            return_raw_response (bool, optional): If True, return raw API response; otherwise return
                processed and sorted trend data. Default is False.

        Returns:
            (dict|list): If return_raw_response is True returns raw API response; otherwise returns
                merged, sorted trend data.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
            ParameterError: If start_time/end_time/duration arguments are invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)

        params = build_trend_params(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            site_id=site_id,
        )
        path = f"{MONITOR_TYPE}/{serial_number}/hardware-trends"
        response = execute_get(central_conn, endpoint=path, params=params)

        return normalize_trend_response(response, return_raw_response)

    @staticmethod
    def get_switch_interface_poe(central_conn, serial_number):
        """
        Get interface PoE details for a specific switch by serial number or stack ID.

        Conductor serial may also be used instead of a stack ID.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch (standalone), stack ID, or conductor
                serial (stacked).

        Returns:
            (dict): API response with interface PoE details.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}/interface-poe"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_switch_vsx(central_conn, serial_number):
        """
        Get Virtual Switching Extension (VSX) details for a specific switch.

        Returns VSX configuration and operational details for the specified switch. If the switch
        does not support VSX or VSX is not configured, the API returns a 200 response with an
        empty VSX object (all fields null).

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.

        Returns:
            (dict): API response with VSX configuration and operational details.

        Raises:
            ParameterError: If central_conn is None or serial_number is missing/invalid.
        """
        validate_central_conn_and_serial(central_conn, serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}/vsx"
        return execute_get(central_conn, endpoint=path)
