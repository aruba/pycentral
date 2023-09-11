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

from pycentral.url_utils import RapidsUrl, urlJoin
from pycentral.base_utils import console_logger
urls = RapidsUrl()


class Rogues():
    """A Python class to obtain Aruba Central's Rougue details via REST APIs.
    """

    def list_rogue_aps(self, conn, group=None, label=None, site=None,
                       swarm_id=None, start=None, end=None,
                       from_timestamp=None, to_timestamp=None, limit=100,
                       offset=0):
        """Get rogue APs over a time period

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: List of group names, defaults to None
        :type group: list, optional
        :param label: List of label names, defaults to None
        :type label: list, optional
        :param site: List of site names, defaults to None
        :type site: list, optional
        :param swarm_id: Filter by Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param start: Need information from this timestamp. Timestamp is epoch\
            in milliseconds.
            Default is current timestamp minus 3 hours, defaults to None
        :type start: int, optional
        :param end: Need information to this timestamp. Timestamp is epoch in\
            milliseconds. Default is current timestamp, defaults to None
        :type end: int, optional
        :param from_timestamp: This parameter supercedes start parameter. Need\
            information from this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp minus 3 hours, defaults to None
        :type from_timestamp: int, optional
        :param to_timestamp: This parameter supercedes end parameter. Need\
            information to this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp, defaults to None
        :type to_timestamp: int, optional
        :param limit: pagination size (default = 100), defaults to 100
        :type limit: int, optional
        :param offset: Pagination offset (default = 0), defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.ROGUES["GET_ROGUE_AP"]
        params = {
            "limit": limit,
            "offset": offset
        }
        if group:
            params["group"] = group
        if label:
            params["label"] = label
        if site:
            params["site"] = site
        if swarm_id:
            params["swarm_id"] = swarm_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        if to_timestamp:
            params["to_timestamp"] = to_timestamp
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def list_interfering_aps(self, conn, group=None, label=None, site=None,
                             swarm_id=None, start=None, end=None,
                             from_timestamp=None, to_timestamp=None, limit=100,
                             offset=0):
        """Get interfering APs over a time period

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
        API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: List of group names, defaults to None
        :type group: list, optional
        :param label: List of label names, defaults to None
        :type label: list, optional
        :param site: List of site names, defaults to None
        :type site: list, optional
        :param swarm_id: Filter by Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param start: Need information from this timestamp. Timestamp is epoch\
            in milliseconds.
            Default is current timestamp minus 3 hours, defaults to None
        :type start: int, optional
        :param end: Need information to this timestamp. Timestamp is epoch in\
            milliseconds.
            Default is current timestamp, defaults to None
        :type end: int, optional
        :param from_timestamp: This parameter supercedes start parameter. Need\
            information from this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp minus 3 hours, defaults to None
        :type from_timestamp: int, optional
        :param to_timestamp: This parameter supercedes end parameter. Need\
            information to this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp, defaults to None
        :type to_timestamp: int, optional
        :param limit: pagination size (default = 100), defaults to 100
        :type limit: int, optional
        :param offset: Pagination offset (default = 0), defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in \
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.ROGUES["GET_INTERFERING_AP"]
        params = {
            "limit": limit,
            "offset": offset
        }
        if group:
            params["group"] = group
        if label:
            params["label"] = label
        if site:
            params["site"] = site
        if swarm_id:
            params["swarm_id"] = swarm_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        if to_timestamp:
            params["to_timestamp"] = to_timestamp
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def list_suspect_aps(self, conn, group=None, label=None, site=None,
                         swarm_id=None, start=None, end=None,
                         from_timestamp=None, to_timestamp=None, limit=100,
                         offset=0):
        """Get suspect APs over a time period

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: List of group names, defaults to None
        :type group: list, optional
        :param label: List of label names, defaults to None
        :type label: list, optional
        :param site: List of site names, defaults to None
        :type site: list, optional
        :param swarm_id: Filter by Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param start: Need information from this timestamp. Timestamp is epoch\
            in milliseconds. Default is current timestamp minus 3 hours,\
            defaults to None
        :type start: int, optional
        :param end: Need information to this timestamp. Timestamp is epoch in\
            milliseconds. Default is current timestamp, defaults to None
        :type end: int, optional
        :param from_timestamp: This parameter supercedes start parameter. Need\
            information from this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp minus 3 hours, defaults to None
        :type from_timestamp: int, optional
        :param to_timestamp: This parameter supercedes end parameter. Need\
            information to this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp, defaults to None
        :type to_timestamp: int, optional
        :param limit: pagination size (default = 100), defaults to 100
        :type limit: int, optional
        :param offset: Pagination offset (default = 0), defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.ROGUES["GET_SUSPECT_AP"]
        params = {
            "limit": limit,
            "offset": offset
        }
        if group:
            params["group"] = group
        if label:
            params["label"] = label
        if site:
            params["site"] = site
        if swarm_id:
            params["swarm_id"] = swarm_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        if to_timestamp:
            params["to_timestamp"] = to_timestamp
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def list_neighbor_aps(self, conn, group=None, label=None, site=None,
                          swarm_id=None, start=None, end=None,
                          from_timestamp=None, to_timestamp=None, limit=100,
                          offset=0):
        """Get neighbor APs over a time period

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: List of group names, defaults to None
        :type group: list, optional
        :param label: List of label names, defaults to None
        :type label: list, optional
        :param site: List of site names, defaults to None
        :type site: list, optional
        :param swarm_id: Filter by Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param start: Need information from this timestamp. Timestamp is epoch\
            in milliseconds. Default is current timestamp minus 3 hours,\
            defaults to None
        :type start: int, optional
        :param end: Need information to this timestamp. Timestamp is epoch in\
            milliseconds. Default is current timestamp, defaults to None
        :type end: int, optional
        :param from_timestamp: This parameter supercedes start parameter. Need\
            information from this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp minus 3 hours, defaults to None
        :type from_timestamp: int, optional
        :param to_timestamp: This parameter supercedes end parameter. Need\
            information to this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp, defaults to None
        :type to_timestamp: int, optional
        :param limit: pagination size (default = 100), defaults to 100
        :type limit: int, optional
        :param offset: Pagination offset (default = 0), defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.ROGUES["GET_NEIGHBOR_AP"]
        params = {
            "limit": limit,
            "offset": offset
        }
        if group:
            params["group"] = group
        if label:
            params["label"] = label
        if site:
            params["site"] = site
        if swarm_id:
            params["swarm_id"] = swarm_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        if to_timestamp:
            params["to_timestamp"] = to_timestamp
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp


class WIDS():
    """A Python Class to obtain Aruba Central's Wireless Intrusion Detection\
        details based on REST APIs.
    """

    def list_client_attacks(self, conn, group=None, label=None, site=None,
                            swarm_id=None, start=None, end=None,
                            from_timestamp=None, to_timestamp=None, limit=100,
                            calculate_total=True, sort="-ts", offset=0):
        """Get client attacks over a time period

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: List of group names, defaults to None
        :type group: list, optional
        :param label: List of label names, defaults to None
        :type label: list, optional
        :param site: List of site names, defaults to None
        :type site: list, optional
        :param swarm_id: Filter by Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param start: Need information from this timestamp. Timestamp is epoch\
            in milliseconds. Default is current timestamp minus 3 hours,\
            defaults to None
        :type start: int, optional
        :param end: Need information to this timestamp. Timestamp is epoch in\
            milliseconds. Default is current timestamp, defaults to None
        :type end: int, optional
        :param from_timestamp: This parameter supercedes start parameter. Need\
            information from this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp minus 3 hours, defaults to None
        :type from_timestamp: int, optional
        :param to_timestamp: This parameter supercedes end parameter. Need\
            information to this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp, defaults to None
        :type to_timestamp: int, optional
        :param limit: pagination size (default = 100), defaults to 100
        :type limit: int, optional
        :param calculate_total: Whether to calculate total client attacks,\
            defaults to True
        :type calculate_total: bool, optional
        :param sort: Sort parameter -ts(sort based on the timestamps in\
            descending), +ts(sort based on timestamps ascending), -macaddr\
            (sort based on station mac descending) and +macaddr(sort based \
            station mac ascending), defaults to "-ts"
        :type sort: str, optional
        :param offset: Pagination offset (default = 0), defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.WIDS["GET_CLIENT_ATTACKS"]
        params = {
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "calculate_total": calculate_total
        }
        if group:
            params["group"] = group
        if label:
            params["label"] = label
        if site:
            params["site"] = site
        if swarm_id:
            params["swarm_id"] = swarm_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        if to_timestamp:
            params["to_timestamp"] = to_timestamp
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def list_infrastructure_attacks(self, conn, group=None, label=None,
                                    site=None, swarm_id=None, start=None,
                                    end=None, from_timestamp=None,
                                    to_timestamp=None, limit=100,
                                    calculate_total=True, sort="-ts",
                                    offset=0):
        """Get infrastructure attacks over a time period

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: List of group names, defaults to None
        :type group: list, optional
        :param label: List of label names, defaults to None
        :type label: list, optional
        :param site: List of site names, defaults to None
        :type site: list, optional
        :param swarm_id: Filter by Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param start: Need information from this timestamp. Timestamp is epoch\
            in milliseconds. Default is current timestamp minus 3 hours,\
            defaults to None
        :type start: int, optional
        :param end: Need information to this timestamp. Timestamp is epoch in\
            milliseconds. Default is current timestamp, defaults to None
        :type end: int, optional
        :param from_timestamp: This parameter supercedes start parameter. Need\
            information from this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp minus 3 hours, defaults to None
        :type from_timestamp: int, optional
        :param to_timestamp: This parameter supercedes end parameter. Need\
            information to this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp, defaults to None
        :type to_timestamp: int, optional
        :param limit: pagination size (default = 100), defaults to 100
        :type limit: int, optional
        :param calculate_total: Whether to calculate total client attacks,\
            defaults to True
        :type calculate_total: bool, optional
        :param sort: Sort parameter -ts(sort based on the timestamps in\
            descending), +ts(sort based on timestamps ascending), -macaddr\
            (sort based on station mac descending) and +macaddr(sort based\
            station mac ascending), defaults to "-ts"
        :type sort: str, optional
        :param offset: Pagination offset (default = 0), defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.WIDS["GET_INFRA_ATTACKS"]
        params = {
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "calculate_total": calculate_total
        }
        if group:
            params["group"] = group
        if label:
            params["label"] = label
        if site:
            params["site"] = site
        if swarm_id:
            params["swarm_id"] = swarm_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        if to_timestamp:
            params["to_timestamp"] = to_timestamp
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def list_wids_attacks(self, conn, group=None, label=None, site=None,
                          swarm_id=None, start=None, end=None,
                          from_timestamp=None, to_timestamp=None, limit=100,
                          sort="-ts", offset=0):
        """Get WIDS events over a time period

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param group: List of group names, defaults to None
        :type group: list, optional
        :param label: List of label names, defaults to None
        :type label: list, optional
        :param site: List of site names, defaults to None
        :type site: list, optional
        :param swarm_id: Filter by Swarm ID, defaults to None
        :type swarm_id: str, optional
        :param start: Need information from this timestamp. Timestamp is epoch\
            in milliseconds. Default is current timestamp minus 3 hours,\
            defaults to None
        :type start: int, optional
        :param end: Need information to this timestamp. Timestamp is epoch in\
            milliseconds. Default is current timestamp, defaults to None
        :type end: int, optional
        :param from_timestamp: This parameter supercedes start parameter. Need\
            information from this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp minus 3 hours, defaults to None
        :type from_timestamp: int, optional
        :param to_timestamp: This parameter supercedes end parameter. Need\
            information to this timestamp. Timestamp is epoch in seconds.\
            Default is current UTC timestamp, defaults to None
        :type to_timestamp: int, optional
        :param limit: pagination size (default = 100), defaults to 100
        :type limit: int, optional
        :param sort: Sort parameter -ts(sort based on the timestamps in\
            descending), +ts(sort based on timestamps ascending), -macaddr\
            (sort based on station mac descending) and +macaddr(sort based\
            station mac ascending), defaults to "-ts"
        :type sort: str, optional
        :param offset: Pagination offset (default = 0), defaults to 0
        :type offset: int, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.WIDS["GET_WIDS_EVENTS"]
        params = {
            "limit": limit,
            "offset": offset,
            "sort": sort
        }
        if group:
            params["group"] = group
        if label:
            params["label"] = label
        if site:
            params["site"] = site
        if swarm_id:
            params["swarm_id"] = swarm_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if from_timestamp:
            params["from_timestamp"] = from_timestamp
        if to_timestamp:
            params["to_timestamp"] = to_timestamp
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp
