from ..utils.monitoring_utils import execute_get, build_timestamp_filter
from ..exceptions import ParameterError


class LocationAnalytics:

    @staticmethod
    def get_trends(central_conn, site_id=None, start_time=None, end_time=None, duration=None):
        """
        Retrieve location analytics trends.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/location-analytics/trends`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str, optional): Site identifier to filter by.
            start_time (str, optional): Start time (RFC3339 or epoch).
            end_time (str, optional): End time (RFC3339 or epoch).
            duration (str, optional): Relative duration (e.g. '3h', '1d').

        Returns:
            (dict): Location analytics trend data.

        Raises:
            ParameterError: If central_conn is None.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        params = {}
        if site_id:
            params["site-id"] = site_id
        if start_time is not None or end_time is not None or duration is not None:
            start_rfc, end_rfc = build_timestamp_filter(
                start_time=start_time, end_time=end_time, duration=duration, fmt="rfc3339"
            )
            params["start-at"] = start_rfc
            params["end-at"] = end_rfc
        return execute_get(central_conn, endpoint="location-analytics/trends", params=params)

    @staticmethod
    def get_site_insights(central_conn, site_id, start_time=None, end_time=None, duration=None):
        """
        Retrieve location analytics insights for a site.

        This method makes an API call to the following endpoint - `GET network-monitoring/v1/location-analytics/sites/{site_id}/insights`

        Args:
            central_conn (NewCentralBase): Central connection object.
            site_id (str): Site identifier.
            start_time (str, optional): Start time (RFC3339 or epoch).
            end_time (str, optional): End time (RFC3339 or epoch).
            duration (str, optional): Relative duration (e.g. '3h', '1d').

        Returns:
            (dict): Site-level location analytics insights.

        Raises:
            ParameterError: If site_id missing.
        """
        if not site_id or not isinstance(site_id, str):
            raise ParameterError("site_id is required and must be a string")
        params = {}
        if start_time is not None or end_time is not None or duration is not None:
            start_rfc, end_rfc = build_timestamp_filter(
                start_time=start_time, end_time=end_time, duration=duration, fmt="rfc3339"
            )
            params["start-at"] = start_rfc
            params["end-at"] = end_rfc
        return execute_get(central_conn, endpoint=f"location-analytics/sites/{site_id}/insights",
                           params=params)
