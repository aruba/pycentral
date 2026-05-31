from ..utils.monitoring_utils import (
    execute_get,
    build_timestamp_filter,
    _validate_mac_address,
)
from ..exceptions import ParameterError
from .constants import CLIENT_LIMIT


class Clients:
    @staticmethod
    def get_all_clients(
        central_conn,
        site_id=None,
        site_name=None,
        serial_number=None,
        filter_str=None,
        sort=None,
        duration=None,
        start_time=None,
        end_time=None,
    ):
        """
        Return all clients based on the provided parameters. Additionally,
        handle pagination.

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            serial_number (str, optional): Device serial number to filter clients.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            duration (str, optional): Relative time window (e.g., '3h', '2d', '1w', '30m').
            start_time (str, optional): Start time (RFC 3339 date-time string).
            end_time (str, optional): End time (RFC 3339 date-time string).

        Returns:
            (list): All client details for the specified parameters.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid.
        """
        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)
        clients = []
        total_clients = None
        next_page = 1
        while True:
            resp = Clients.get_clients(
                central_conn=central_conn,
                site_id=site_id,
                site_name=site_name,
                serial_number=serial_number,
                filter_str=filter_str,
                sort=sort,
                next_page=next_page,
                limit=CLIENT_LIMIT,
                duration=duration,
                start_time=start_time,
                end_time=end_time,
            )
            if total_clients is None:
                total_clients = resp.get("total", 0)
            clients.extend(resp.get("items", []))
            if len(clients) == total_clients:
                break
            next_val = resp.get("next")
            if not next_val:
                break
            next_page = int(next_val)
        return clients

    @staticmethod
    def get_wireless_clients(
        central_conn,
        site_id=None,
        site_name=None,
        serial_number=None,
        sort=None,
        duration=None,
        start_time=None,
        end_time=None,
    ):
        """
        Fetch all wireless clients. Optionally fetch by site/device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            serial_number (str, optional): Device serial number to query.
            sort (str, optional): Optional sort expression.
            duration (str, optional): Relative time window (e.g., '3h', '2d', '1w', '30m').
            start_time (str, optional): Start time (RFC 3339 date-time string).
            end_time (str, optional): End time (RFC 3339 date-time string).

        Returns:
            (list): List of wireless clients.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid.
        """
        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)
        return Clients.get_all_clients(
            central_conn=central_conn,
            site_id=site_id,
            site_name=site_name,
            serial_number=serial_number,
            filter_str="clientConnectionType eq 'Wireless'",
            sort=sort,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
        )

    @staticmethod
    def get_wired_clients(
        central_conn,
        site_id=None,
        site_name=None,
        serial_number=None,
        sort=None,
        duration=None,
        start_time=None,
        end_time=None,
    ):
        """
        Fetch all wired clients. Optionally fetch by site/device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            serial_number (str, optional): Device serial number to query.
            sort (str, optional): Optional sort expression.
            duration (str, optional): Relative time window (e.g., '3h', '2d', '1w', '30m').
            start_time (str, optional): Start time (RFC 3339 date-time string).
            end_time (str, optional): End time (RFC 3339 date-time string).

        Returns:
            (list): List of wired clients.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid.
        """
        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)
        return Clients.get_all_clients(
            central_conn=central_conn,
            site_id=site_id,
            site_name=site_name,
            serial_number=serial_number,
            filter_str="clientConnectionType eq 'Wired'",
            sort=sort,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
        )

    @staticmethod
    def get_clients_associated_device(central_conn, serial_number):
        """
        Fetch all clients associated with a specific device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Device serial number to filter clients.

        Returns:
            (list): Clients associated with the specified device.
        """
        return Clients.get_all_clients(
            central_conn=central_conn,
            serial_number=serial_number,
        )

    @staticmethod
    def get_connected_clients(
        central_conn, site_id=None, site_name=None, serial_number=None
    ):
        """
        Fetch all connected clients. Optionally fetch by site/device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            serial_number (str, optional): Device serial number to query.

        Returns:
            (list[dict]): List of connected clients.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid.
        """
        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)
        return Clients.get_all_clients(
            central_conn=central_conn,
            site_id=site_id,
            site_name=site_name,
            serial_number=serial_number,
            filter_str="status eq 'Connected'",
        )

    @staticmethod
    def get_failed_clients(
        central_conn, site_id=None, site_name=None, serial_number=None
    ):
        """
        Fetch all failed clients. Optionally fetch by site/device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            serial_number (str, optional): Device serial number to query.

        Returns:
            (list[dict]): List of failed clients.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid.
        """
        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)
        return Clients.get_all_clients(
            central_conn=central_conn,
            site_id=site_id,
            site_name=site_name,
            serial_number=serial_number,
            filter_str="status eq 'Failed'",
        )

    @staticmethod
    def get_clients(
        central_conn,
        site_id=None,
        site_name=None,
        serial_number=None,
        filter_str=None,
        sort=None,
        next_page=1,
        limit=CLIENT_LIMIT,
        duration=None,
        start_time=None,
        end_time=None,
    ):
        """
        Fetch clients based on provided parameters. Additionally, handles
        pagination.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/clients`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            serial_number (str, optional): Device serial number to query.
            filter_str (str, optional): Optional filter expression (supported fields documented in API Reference Guide).
            sort (str, optional): Optional sort parameter (supported fields documented in API Reference Guide).
            next_page (int, optional): Page token/index for pagination.
            limit (int, optional): Maximum number of items to return.
            duration (str, optional): Relative time window (e.g., '3h', '2d', '1w', '30m').
            start_time (str, optional): Start time (RFC 3339 date-time string).
            end_time (str, optional): End time (RFC 3339 date-time string).

        Returns:
            (dict): Raw API response containing keys like 'items', 'total', and 'next'.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid.
        """
        path = "clients"

        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)
        params = {
            "site-id": site_id,
            "site-name": site_name,
            "serial-number": serial_number,
            "filter": filter_str,
            "sort": sort,
            "next": next_page,
            "limit": limit,
        }
        if start_time is None and end_time is None and duration is None:
            return execute_get(central_conn, endpoint=path, params=params)

        params = Clients._time_filter(
            params=params,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
        )

        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_client_trends(
        central_conn,
        site_id=None,
        site_name=None,
        group_by=None,
        client_type=None,
        serial_number=None,
        start_time=None,
        end_time=None,
        duration=None,
        return_raw_response=False,
    ):
        """
        Fetch client trend data. Optionally fetch by site/device.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/clients-trend`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            group_by (str, optional): Dimension to group results by (e.g., 'mac', 'ap').
            client_type (str, optional): Trend type (passed as 'type' in the request).
            serial_number (str, optional): Device serial number to query.
            start_time (str, optional): Start time (RFC 3339 date-time string).
            end_time (str, optional): End time (RFC 3339 date-time string).
            duration (str, optional): Relative time window (e.g., '3h', '2d', '1w', '30m').
            return_raw_response (bool, optional): If True, return the raw API payload.

        Returns:
            (list[dict] or dict): Processed list of timestamped samples, or raw response if requested.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid.
        """
        path = "clients-trend"

        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)
        params = {
            "site-id": site_id,
            "site-name": site_name,
            "group-by": group_by,
            "type": client_type,
            "serial-number": serial_number,
        }

        if (
            start_time is not None
            or end_time is not None
            or duration is not None
        ):
            params = Clients._time_filter(
                params=params,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )

        response = execute_get(central_conn, endpoint=path, params=params)
        if return_raw_response:
            return response

        return Clients._process_client_trend_samples(response)

    @staticmethod
    def get_top_n_clients(
        central_conn,
        site_id=None,
        site_name=None,
        serial_number=None,
        limit=100,
        start_time=None,
        end_time=None,
        duration=None,
    ):
        """
        Fetch the top-N clients by usage. Optionally fetch by site/device.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/clients-topn-usage`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str|int, optional): Identifier of the site to query.
            site_name (str, optional): Name of the site to query.
            serial_number (str, optional): Device serial number to query.
            limit (int, optional): Number of top clients to return (1..100).
            start_time (str, optional): Start time (RFC 3339 date-time string).
            end_time (str, optional): End time (RFC 3339 date-time string).
            duration (str, optional): Relative time window (e.g., '3h', '2d', '1w', '30m').

        Returns:
            (dict): Raw API response containing top-N usage data.

        Raises:
            ParameterError: If site_id or site_name is provided but invalid, or if limit is not in range 1..100.
        """
        path = "clients-topn-usage"
        if site_id or site_name:
            Clients._validate_site_id(site_id, site_name)

        if limit is not None and (limit > 100 or limit < 1):
            raise ParameterError("Limit must be between 1 and 100")

        params = {
            "site-id": site_id,
            "site-name": site_name,
            "serial-number": serial_number,
            "limit": limit,
        }

        if start_time is None and end_time is None and duration is None:
            return execute_get(central_conn, endpoint=path, params=params)

        params = Clients._time_filter(
            params=params,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
        )

        return execute_get(central_conn, endpoint=path, params=params)

    @staticmethod
    def get_client_details(
        central_conn,
        client_mac,
    ):
        """
        Fetch details for a specific client by MAC address.
        This method makes an API call to the following endpoint - `GET network-monitoring/v1/clients/{client_mac}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            client_mac (str): MAC address of the client to query.

        Returns:
            (dict): Client details as returned by the API.
        """
        _validate_mac_address(client_mac)

        path = f"clients/{client_mac}"
        return execute_get(central_conn, endpoint=path)

    @staticmethod
    def _time_filter(params, start_time, end_time, duration):
        """
        Apply a time filter to params using RFC 3339 timestamps.

        Args:
            params (dict): Existing query params to augment.
            start_time (str|None): Start time (RFC 3339 date-time string).
            end_time (str|None): End time (RFC 3339 date-time string).
            duration (str|None): Relative time window (e.g., '3h', '2d', '1w', '30m').

        Returns:
            (dict): Params augmented with 'start-at' and 'end-at'.

        Note:
            Internal SDK function
        """
        start_rfc, end_rfc = build_timestamp_filter(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            fmt="rfc3339",
        )
        params["start-at"] = start_rfc
        params["end-at"] = end_rfc
        return params

    @staticmethod
    def _process_client_trend_samples(payload):
        """
        Normalize client trend payload into a list of timestamped dicts.

        Args:
            payload (dict): Raw trend payload with 'categories' and 'samples'.

        Returns:
            (list[dict]): Normalized rows with 'timestamp' and category/value pairs.

        Note:
            Internal SDK function
        """
        categories = payload.get("categories", [])
        samples = payload.get("samples", [])
        out = []
        for s in samples:
            row = {"timestamp": s.get("ts") or s.get("timestamp")}
            vals = s.get("data")
            if isinstance(vals, (list, tuple)):
                for cat, val in zip(categories, vals):
                    row[cat] = val
            else:
                if categories:
                    row[categories[0]] = vals
                else:
                    row["value"] = vals
            out.append(row)
        return out

    @staticmethod
    def _validate_site_id(site_id=None, site_name=None):
        """
        Validate that at least one site identifier is provided.

        Args:
            site_id (str|int, optional): Site identifier to validate.
            site_name (str, optional): Site name to validate.

        Raises:
            ParameterError: If site_id and site_name are not provided or invalid.

        Note:
            Internal SDK function
        """
        if site_id is None and site_name is None:
            raise ParameterError(
                "either site_id or site_name must be provided"
            )

        if site_id is not None and (
            not isinstance(site_id, (str, int)) or not site_id
        ):
            raise ParameterError(
                "site_id must be a non-empty string or integer"
            )

        if site_name is not None and (
            not isinstance(site_name, str) or not site_name
        ):
            raise ParameterError("site_name must be a non-empty string")
