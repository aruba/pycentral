# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.monitoring_utils import execute_get
from ..utils.url_utils import generate_url
from ..exceptions import ParameterError

REPORT_LIMIT = 100
REPORTS_ENDPOINT = "reports"


class Reporting:

    @staticmethod
    def list_reports(central_conn, filter_str=None, sort=None, limit=REPORT_LIMIT, next_page=1):
        """Retrieve a page of saved reports.

        This method makes an API call to the following endpoint -
        ``GET network-monitoring/v1alpha1/reports``

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.
            limit (int, optional): Max results per page (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response with 'items', 'total', 'next'.

        Raises:
            ParameterError: If limit or next_page invalid.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if limit > REPORT_LIMIT:
            raise ParameterError(f"limit cannot exceed {REPORT_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {"filter": filter_str, "sort": sort, "limit": limit, "next": next_page}
        return execute_get(central_conn, endpoint=REPORTS_ENDPOINT, params=params, version="v1alpha1")

    @staticmethod
    def get_all_reports(central_conn, filter_str=None, sort=None):
        """Retrieve all saved reports, handling pagination automatically.

        Args:
            central_conn (NewCentralBase): Central connection object.
            filter_str (str, optional): OData filter expression.
            sort (str, optional): Sort expression.

        Returns:
            (list): All report items across all pages.
        """
        reports = []
        total = None
        next_page = 1
        while True:
            resp = Reporting.list_reports(central_conn, filter_str=filter_str, sort=sort,
                                          limit=REPORT_LIMIT, next_page=next_page)
            if total is None:
                total = resp.get("total", 0)
            reports.extend(resp.get("items", []))
            if len(reports) >= total:
                break
            next_val = resp.get("next")
            if not next_val:
                break
            next_page = int(next_val)
        return reports

    @staticmethod
    def create_report(central_conn, name, report_type, **kwargs):
        """Create a new scheduled report.

        This method makes an API call to the following endpoint -
        ``POST network-monitoring/v1alpha1/reports``

        Args:
            central_conn (NewCentralBase): Central connection object.
            name (str): Report name.
            report_type (str): Report type.
            **kwargs: Additional report fields (schedule, filters, etc. per API spec).

        Returns:
            (dict): API response with the created report.

        Raises:
            ParameterError: If required fields missing.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not name or not isinstance(name, str):
            raise ParameterError("name is required and must be a string")
        if not report_type or not isinstance(report_type, str):
            raise ParameterError("report_type is required and must be a string")
        body = {"name": name, "type": report_type, **kwargs}
        path = generate_url(REPORTS_ENDPOINT, "monitoring", "v1alpha1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data=body)
        if resp["code"] not in (200, 201):
            raise Exception(f"Error creating report: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def get_report(central_conn, report_id):
        """Retrieve a specific report.

        This method makes an API call to the following endpoint -
        ``GET network-monitoring/v1alpha1/reports/{report_id}``

        Args:
            central_conn (NewCentralBase): Central connection object.
            report_id (str): Report identifier.

        Returns:
            (dict): Report details.

        Raises:
            ParameterError: If report_id missing.
        """
        if not report_id or not isinstance(report_id, str):
            raise ParameterError("report_id is required and must be a string")
        return execute_get(central_conn, endpoint=f"{REPORTS_ENDPOINT}/{report_id}", version="v1alpha1")

    @staticmethod
    def update_report(central_conn, report_id, **kwargs):
        """Update a saved report.

        This method makes an API call to the following endpoint -
        ``PUT network-monitoring/v1alpha1/reports/{report_id}``

        Args:
            central_conn (NewCentralBase): Central connection object.
            report_id (str): Report identifier.
            **kwargs: Fields to update.

        Returns:
            (dict): API response.

        Raises:
            ParameterError: If report_id missing.
        """
        if not report_id or not isinstance(report_id, str):
            raise ParameterError("report_id is required and must be a string")
        path = generate_url(f"{REPORTS_ENDPOINT}/{report_id}", "monitoring", "v1alpha1")
        resp = central_conn.command(api_method="PUT", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(f"Error updating report {report_id}: {resp['code']} - {resp['msg']}")
        return resp["msg"]

    @staticmethod
    def delete_report(central_conn, report_id):
        """Delete a saved report.

        This method makes an API call to the following endpoint -
        ``DELETE network-monitoring/v1alpha1/reports/{report_id}``

        Args:
            central_conn (NewCentralBase): Central connection object.
            report_id (str): Report identifier.

        Returns:
            (bool): True if deleted successfully.

        Raises:
            ParameterError: If report_id missing.
        """
        if not report_id or not isinstance(report_id, str):
            raise ParameterError("report_id is required and must be a string")
        path = generate_url(f"{REPORTS_ENDPOINT}/{report_id}", "monitoring", "v1alpha1")
        resp = central_conn.command(api_method="DELETE", api_path=path)
        if resp["code"] != 200:
            raise Exception(f"Error deleting report {report_id}: {resp['code']} - {resp['msg']}")
        return True

    @staticmethod
    def list_report_runs(central_conn, report_id, limit=REPORT_LIMIT, next_page=1):
        """List execution runs for a report.

        This method makes an API call to the following endpoint -
        ``GET network-monitoring/v1alpha1/reports/{report_id}/runs``

        Args:
            central_conn (NewCentralBase): Central connection object.
            report_id (str): Report identifier.
            limit (int, optional): Max results per page (default 100).
            next_page (int, optional): Pagination cursor (default 1).

        Returns:
            (dict): API response with run history.

        Raises:
            ParameterError: If report_id missing or limit/next_page invalid.
        """
        if not report_id or not isinstance(report_id, str):
            raise ParameterError("report_id is required and must be a string")
        if limit > REPORT_LIMIT:
            raise ParameterError(f"limit cannot exceed {REPORT_LIMIT}")
        if next_page < 1:
            raise ParameterError("next_page must be 1 or greater")
        params = {"limit": limit, "next": next_page}
        return execute_get(central_conn, endpoint=f"{REPORTS_ENDPOINT}/{report_id}/runs",
                          params=params, version="v1alpha1")
