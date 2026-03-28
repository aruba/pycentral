from ..utils.url_utils import generate_url
from ..utils.monitoring_utils import build_timestamp_filter
from ..exceptions import ParameterError

ALERT_LIMIT = 100


class Alerts:
    @staticmethod
    def get_all_alerts(
        central_conn,
        filter_str=None,
        sort=None,
        severity=None,
        start_time=None,
        end_time=None,
        duration=None,
    ):
        """Retrieve all alerts, handling pagination automatically.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            severity (str, optional): Filter by severity (e.g. 'Critical', 'Major',
                'Minor', 'Warning').
            start_time (str, optional): Start time as RFC3339 string or Unix epoch.
            end_time (str, optional): End time as RFC3339 string or Unix epoch.
            duration (str, optional): Relative duration (e.g. '3h', '1d').

        Returns:
            (list): All alert items across all pages.
        """
        alerts = []
        total = None
        next_page = 1
        while True:
            resp = Alerts.get_alerts(
                central_conn,
                filter_str=filter_str,
                sort=sort,
                severity=severity,
                limit=ALERT_LIMIT,
                next_page=next_page,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )
            if total is None:
                total = resp.get("total", 0)
            alerts.extend(resp.get("items", []))
            if len(alerts) >= total:
                break
            next_val = resp.get("next")
            if not next_val:
                break
            next_page = int(next_val)
        return alerts

    @staticmethod
    def get_alerts(
        central_conn,
        filter_str=None,
        sort=None,
        severity=None,
        limit=ALERT_LIMIT,
        next_page=1,
        start_time=None,
        end_time=None,
        duration=None,
    ):
        """Retrieve a page of alerts.

        This method makes an API call to the following endpoint -
        ``GET network-notifications/v1/alerts``

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            severity (str, optional): Filter by severity (e.g. 'Critical', 'Major',
                'Minor', 'Warning').
            limit (int, optional): Max results per page (default 100, max 100).
            next_page (int, optional): Pagination cursor (default 1).
            start_time (str, optional): Start time as RFC3339 string or Unix epoch.
            end_time (str, optional): End time as RFC3339 string or Unix epoch.
            duration (str, optional): Relative duration (e.g. '3h', '1d').

        Returns:
            (dict): API response containing 'items', 'total', and 'next' keys.

        Raises:
            ParameterError: If central_conn is None, limit exceeds ALERT_LIMIT,
                or next_page is less than 1.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > ALERT_LIMIT:
            raise ParameterError(f"limit cannot exceed {ALERT_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")

        params = {
            "filter": filter_str,
            "sort": sort,
            "severity": severity,
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

        path = generate_url("alerts", "notifications", "v1")
        resp = central_conn.command("GET", path, api_params=params)
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving alerts from {path}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def get_alert_details(central_conn, alert_id):
        """Retrieve details for a specific alert.

        This method makes an API call to the following endpoint -
        ``GET network-notifications/v1/alerts/{alert_id}``

        Args:
            central_conn (NewCentralBase): Central connection object.
            alert_id (str): Alert identifier.

        Returns:
            (dict): Alert details as returned by the API.

        Raises:
            ParameterError: If central_conn is None or alert_id is missing or
                not a string.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not alert_id or not isinstance(alert_id, str):
            raise ParameterError("alert_id is required and must be a string")

        path = generate_url(f"alerts/{alert_id}", "notifications", "v1")
        resp = central_conn.command("GET", path, api_params={})
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving alert {alert_id}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]
