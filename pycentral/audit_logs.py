# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pycentral.url_utils import AuditUrl, urlJoin
from pycentral.base_utils import console_logger

urls = AuditUrl()


class Audit:
    """Get the audit logs and event logs with the functions in this class."""

    def get_traillogs(self, conn, limit=100, offset=0, username=None,
                      start_time=None, end_time=None, description=None,
                      target=None, classification=None, customer_name=None,
                      ip_address=None, app_id=None):
        """Get audit logs, sort by time in in reverse chronological order.
        This API returns the first 10,000 results only. Please use filter
        in the API for more relevant results. MSP Customer Would see logs
        of MSP's and tenants as well.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param limit: Maximum number of audit events to be returned, defaults\
            to 100
        :type limit: int, optional
        :param offset: Number of items to be skipped before returning the \
            data, useful for pagination, defaults to 0
        :type offset: int, optional
        :param username: Filter audit logs by User Name, defaults to None
        :type username: str, optional
        :param start_time: Filter audit logs by Time Range. Start time of the\
            audit logs should be provided in epoch seconds, defaults to None
        :type start_time: int, optional
        :param end_time: Filter audit logs by Time Range. End time of the \
            audit logs should be provided in epoch seconds, defaults to None
        :type end_time: int, optional
        :param description: Filter audit logs by Description, defaults to \
            None
        :type description: str, optional
        :param target: Filter audit logs by target, defaults to None
        :type target: str, optional
        :param classification: Filter audit logs by Classification, defaults \
            to None
        :type classification: str, optional
        :param customer_name: Filter audit logs by Customer NameFilter audit \
            logs by Customer Name, defaults to None
        :type customer_name: str, optional
        :param ip_address: Filter audit logs by IP Address, defaults to None
        :type ip_address: str, optional
        :param app_id: Filter audit logs by app_id, defaults to None
        :type app_id: str, optional
        :return: HTTP Response as provided by 'command' function in \
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.TRAIL_LOG["GET_ALL"]
        params = {"limit": limit, "offset": offset}
        if username:
            params["username"] = username
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if description:
            params["description"] = description
        if target:
            params["target"] = target
        if classification:
            params["classification"] = classification
        if customer_name:
            params["customer_name"] = customer_name
        if ip_address:
            params["ip_address"] = ip_address
        if app_id:
            params["app_id"] = app_id
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_traillogs_detail(self, conn, id):
        """Get details of an audit log

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param id: ID of audit event
        :type id: str
        :return: HTTP Response as provided by 'command' function in \
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.TRAIL_LOG["GET"], id)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def get_eventlogs(self, conn, limit=100, offset=0, group_name=None,
                      device_id=None, classification=None, start_time=None,
                      end_time=None):
        """Get audit events for all groups, sort by time in in reverse\
            chronological order.This API returns the first 10,000 results\
            only. Please use filter in the API for more relevant results.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param limit: Maximum number of audit events to be returned, defaults\
            to 100
        :type limit: int, optional
        :param offset: Number of items to be skipped before returning the\
            data, useful for pagination, defaults to 0
        :type offset: int, optional
        :param group_name: Filter audit events by Group Name, defaults to None
        :type group_name: str, optional
        :param device_id: Filter audit events by Target / Device ID. Device ID\
            for AP is VC Name and Serial Number
            for Switches, defaults to None
        :type device_id: str, optional
        :param classification: Filter audit events by classification, defaults\
            to None
        :type classification: str, optional
        :param start_time: Filter audit logs by Time Range. Start time of the\
            audit logs should be provided
            in epoch seconds, defaults to None
        :type start_time: int, optional
        :param end_time: Filter audit logs by Time Range. End time of the\
            audit logs should be provided in epoch
            seconds, defaults to None
        :type end_time: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.EVENT_LOG["GET_ALL"]
        params = {"limit": limit, "offset": offset}
        if group_name:
            params["group_name"] = group_name
        if device_id:
            params["device_id"] = device_id
        if classification:
            params["classification"] = classification
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_eventlogs_detail(self, conn, id):
        """Get details of an audit event/log

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param id: ID of audit event
        :type id: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.EVENT_LOG["GET"], id)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp
