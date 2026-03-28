from ..utils.monitoring_utils import (
    execute_get,
    generate_timestamp_str,
    clean_raw_trend_data,
    merged_dict_to_sorted_list,
)
from ..exceptions import ParameterError
from concurrent.futures import ThreadPoolExecutor, as_completed

SWITCH_LIMIT = 100
MONITOR_TYPE = "switches"


class MonitoringSwitches:
    @staticmethod
    def get_all_switches(central_conn, filter_str=None, sort=None):
        """
        Retrieve all switches, handling pagination automatically.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).

        Returns:
            (list[dict]): List of switch items.
        """
        switches = []
        total_switches = None
        next_page = 1
        while True:
            resp = MonitoringSwitches.get_switches(
                central_conn,
                filter_str=filter_str,
                sort=sort,
                limit=SWITCH_LIMIT,
                next_page=next_page,
            )
            if total_switches is None:
                total_switches = resp.get("total", 0)

            switches.extend(resp["items"])

            if len(switches) == total_switches:
                break

            next_page = resp.get("next")
            if not next_page:
                break

            next_page = int(next_page)
        return switches

    @staticmethod
    def get_switches(
        central_conn, filter_str=None, sort=None, limit=SWITCH_LIMIT, next_page=1
    ):
        """
        Retrieve a single page of switches.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the switches endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If limit or next_page values are invalid.
        """
        path = MONITOR_TYPE
        if limit > SWITCH_LIMIT:
            raise ParameterError(f"limit cannot exceed {SWITCH_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {
            "filter": filter_str,
            "sort": sort,
            "limit": limit,
            "next": next_page,
        }
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_switch_details(central_conn, serial_number):
        """
        Get details for a specific switch.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches/{serial-number}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.

        Returns:
            (dict): API response with switch details.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        MonitoringSwitches._validate_device_serial(serial_number=serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_switch_ports(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
        limit=100,
        next_page=1,
    ):
        """
        Retrieve a list of ports for a specific switch.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches/{serial-number}/ports`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the switch ports endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If serial_number is missing/invalid or limit/next_page values are invalid.
        """
        MonitoringSwitches._validate_device_serial(serial_number=serial_number)
        if limit > 100:
            raise ParameterError("limit cannot exceed 100")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        path = f"{MONITOR_TYPE}/{serial_number}/ports"
        params = {
            "filter": filter_str,
            "sort": sort,
            "limit": limit,
            "next": next_page,
        }
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_switch_port_details(central_conn, serial_number, port_id):
        """
        Get details for a specific port on a switch.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches/{serial-number}/ports/{port-id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.
            port_id (str): Port identifier.

        Returns:
            (dict): API response with port details.

        Raises:
            ParameterError: If serial_number is missing/invalid or port_id is missing/invalid.
        """
        MonitoringSwitches._validate_device_serial(serial_number=serial_number)
        if not isinstance(port_id, str) or not port_id:
            raise ParameterError("port_id is required and must be a string")
        path = f"{MONITOR_TYPE}/{serial_number}/ports/{port_id}"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_switch_cpu_utilization(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
    ):
        """
        Retrieve CPU utilization trends for a switch.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches/{serial-number}/cpu-utilization-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string or seconds for relative queries.

        Returns:
            (dict|list): API response for cpu-utilization-trends.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        MonitoringSwitches._validate_device_serial(serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}/cpu-utilization-trends"
        if start_time is None and end_time is None and duration is None:
            return execute_get(central_conn, endpoint=path)

        return execute_get(
            central_conn,
            endpoint=path,
            params={
                "filter": generate_timestamp_str(
                    start_time=start_time, end_time=end_time, duration=duration
                )
            },
        )

    @staticmethod
    def get_switch_memory_utilization(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
    ):
        """
        Retrieve memory utilization trends for a switch.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches/{serial-number}/memory-utilization-trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string or seconds for relative queries.

        Returns:
            (dict|list): API response for memory-utilization-trends.

        Raises:
            ParameterError: If serial_number is missing/invalid.
        """
        MonitoringSwitches._validate_device_serial(serial_number)
        path = f"{MONITOR_TYPE}/{serial_number}/memory-utilization-trends"
        if start_time is None and end_time is None and duration is None:
            return execute_get(central_conn, endpoint=path)

        return execute_get(
            central_conn,
            endpoint=path,
            params={
                "filter": generate_timestamp_str(
                    start_time=start_time, end_time=end_time, duration=duration
                )
            },
        )

    @staticmethod
    def get_switch_stats(
        central_conn,
        serial_number,
        start_time=None,
        end_time=None,
        duration=None,
        return_raw_response=False,
    ):
        """
        Collect multiple statistics (CPU, memory) for a switch for the specified time range. Default is to return sorted trend statistics for last 3 hours.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.
            start_time (int, optional): Start time (epoch seconds) for range queries.
            end_time (int, optional): End time (epoch seconds) for range queries.
            duration (str|int, optional): Duration string (e.g. '5m') or seconds for relative queries.
            return_raw_response (bool, optional): If True, return raw per-metric responses.

        Returns:
            (list|dict): If return_raw_response is True returns raw list of responses; otherwise returns merged, sorted trend statistics for the switch.

        Raises:
            ParameterError: If serial_number is missing/invalid.
            RuntimeError: If any of the parallel metric requests fail.
        """
        MonitoringSwitches._validate_device_serial(serial_number)

        # dispatch the two metric calls in parallel; helper methods handle timestamp logic
        funcs = [
            MonitoringSwitches.get_switch_cpu_utilization,
            MonitoringSwitches.get_switch_memory_utilization,
        ]

        raw_results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_map = {
                executor.submit(
                    func,
                    central_conn,
                    serial_number,
                    start_time,
                    end_time,
                    duration,
                ): func
                for func in funcs
            }
            for fut in as_completed(future_map):
                func = future_map[fut]
                try:
                    resp = fut.result()
                    raw_results.append(resp)
                except Exception as e:
                    # propagate the error for the caller to handle, but include which call failed
                    raise RuntimeError(
                        f"{func.__name__} metrics request failed: {e}"
                    ) from e

        if return_raw_response:
            return raw_results

        data = {}
        for resp in raw_results:
            if not isinstance(resp, dict):
                continue
            data = clean_raw_trend_data(resp, data=data)
        data = merged_dict_to_sorted_list(data)
        return data

    @staticmethod
    def get_switch_stacks(
        central_conn, filter_str=None, sort=None, limit=100, next_page=1
    ):
        """
        Retrieve a list of switch stacks.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switch-stacks`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the switch-stacks endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If limit or next_page values are invalid.
        """
        path = "switch-stacks"
        if limit > 100:
            raise ParameterError("limit cannot exceed 100")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {
            "filter": filter_str,
            "sort": sort,
            "limit": limit,
            "next": next_page,
        }
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_switch_stack_details(central_conn, stack_id):
        """
        Get details for a specific switch stack.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switch-stacks/{stack-id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            stack_id (str): Identifier of the switch stack.

        Returns:
            (dict): API response with switch stack details.

        Raises:
            ParameterError: If stack_id is missing/invalid.
        """
        if not isinstance(stack_id, str) or not stack_id:
            raise ParameterError("stack_id is required and must be a string")
        path = f"switch-stacks/{stack_id}"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def get_switch_vlans(
        central_conn,
        serial_number,
        filter_str=None,
        sort=None,
        limit=100,
        next_page=1,
    ):
        """
        Retrieve a list of VLANs for a specific switch.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/switches/{serial-number}/vlans`

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the switch.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            limit (int, optional): Number of entries to return (default is 100).
            next_page (int, optional): Pagination cursor/index for next page (default is 1).

        Returns:
            (dict): API response for the switch VLANs endpoint (contains 'items', 'total', etc.).

        Raises:
            ParameterError: If serial_number is missing/invalid or limit/next_page values are invalid.
        """
        MonitoringSwitches._validate_device_serial(serial_number=serial_number)
        if limit > 100:
            raise ParameterError("limit cannot exceed 100")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        path = f"{MONITOR_TYPE}/{serial_number}/vlans"
        params = {
            "filter": filter_str,
            "sort": sort,
            "limit": limit,
            "next": next_page,
        }
        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def _validate_device_serial(serial_number):
        """
        Validate switch device serial_number.

        Args:
            serial_number (str): Device serial number to validate.

        Raises:
            ParameterError: If serial_number is missing or not a string.

        Note:
            Internal SDK function
        """
        if not isinstance(serial_number, str) or not serial_number:
            raise ParameterError(
                "serial_number is required and must be a string"
            )
