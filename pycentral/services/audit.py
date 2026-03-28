# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.url_utils import generate_url
from ..utils.monitoring_utils import build_timestamp_filter
from ..exceptions import ParameterError

AUDIT_ENDPOINT = "audit"
AUDIT_LIMIT = 100


class AuditTrail:
    @staticmethod
    def get_audit_events(
        central_conn,
        filter_str=None,
        sort=None,
        limit=100,
        next_page=1,
        start_time=None,
        end_time=None,
        duration=None,
    ):
        """Retrieve audit trail events.

        This method makes an API call to the following endpoint - `GET network-services/v1/audit`

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Max results per page (default 100).
            next_page (int, optional): Pagination cursor (default 1).
            start_time (str, optional): Start time as RFC3339 string or Unix epoch
                (ms or s). Must be provided together with end_time.
            end_time (str, optional): End time as RFC3339 string or Unix epoch
                (ms or s). Must be provided together with start_time.
            duration (str, optional): Relative duration string (e.g. '3h', '1d', '1w').
                Cannot be combined with start_time/end_time.

        Returns:
            (dict): API response containing audit event items, total count, and
                pagination cursor.

        Raises:
            ParameterError: If central_conn is None, limit exceeds 100, or next_page
                is less than 1.
            ValueError: If invalid time range parameters are provided.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > AUDIT_LIMIT:
            raise ParameterError(f"limit cannot exceed {AUDIT_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")

        params = {
            "filter": filter_str,
            "sort": sort,
            "limit": limit,
            "next": next_page,
        }

        if start_time is not None or end_time is not None or duration is not None:
            start_rfc, end_rfc = build_timestamp_filter(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                fmt="rfc3339",
            )
            params["start-at"] = start_rfc
            params["end-at"] = end_rfc

        path = generate_url(AUDIT_ENDPOINT, "services", "v1")
        resp = central_conn.command("GET", path, api_params=params)
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving audit events from {path}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def get_all_audit_events(
        central_conn,
        filter_str=None,
        sort=None,
        start_time=None,
        end_time=None,
        duration=None,
    ):
        """Retrieve all audit events, handling pagination automatically.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            start_time (str, optional): Start time as RFC3339 string or Unix epoch
                (ms or s). Must be provided together with end_time.
            end_time (str, optional): End time as RFC3339 string or Unix epoch
                (ms or s). Must be provided together with start_time.
            duration (str, optional): Relative duration string (e.g. '3h', '1d', '1w').
                Cannot be combined with start_time/end_time.

        Returns:
            (list): All audit event items across all pages.

        Raises:
            ParameterError: If central_conn is None.
            ValueError: If invalid time range parameters are provided.
        """
        events = []
        total = None
        next_page = 1
        while True:
            resp = AuditTrail.get_audit_events(
                central_conn,
                filter_str=filter_str,
                sort=sort,
                limit=AUDIT_LIMIT,
                next_page=next_page,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )
            if total is None:
                total = resp.get("total", 0)

            events.extend(resp.get("items", []))

            if total is not None and len(events) >= total:
                break

            next_val = resp.get("next")
            if not next_val:
                break
            next_page = int(next_val)
        return events

    @staticmethod
    def get_audit_event_details(central_conn, event_id):
        """Retrieve details for a specific audit event.

        This method makes an API call to the following endpoint - `GET network-services/v1/audit/{event_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            event_id (str): Unique identifier of the audit event.

        Returns:
            (dict): Audit event details as returned by the API.

        Raises:
            ParameterError: If central_conn is None or event_id is missing or not a string.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not event_id or not isinstance(event_id, str):
            raise ParameterError("event_id is required and must be a non-empty string")

        path = generate_url(f"{AUDIT_ENDPOINT}/{event_id}", "services", "v1")
        resp = central_conn.command("GET", path, api_params={})
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving audit event {event_id}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]
