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

from pycentral.url_utils import TopoUrl, urlJoin
from pycentral.base_utils import console_logger
urls = TopoUrl()


class Topology():
    """A python class to obtain Aruba Central Site's topology details via REST\
        APIs.
    """

    def get_topology(self, conn, site_id):
        """Get topology details of a site. The input is the id corresponding\
        to a label or a site.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_id: Site ID
        :type site_id: int
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.TOPOLOGY["GET_TOPO_SITE"], str(site_id))
        print(path)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def get_device_details(self, conn, device_serial):
        """Provides details of a device when serial number is passed as input.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Device Serial Number
        :type device_serial: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.TOPOLOGY["GET_DEVICES"], device_serial)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def get_edge_details(self, conn, source_serial, dest_serial):
        """Get details of an edge grouped by lagname. The serials of\
        nodes/devices on both sides of the edge should passed as input.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param source_serial: Device serial number.
        :type source_serial: str
        :param dest_serial: Device serial number.
        :type dest_serial: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.TOPOLOGY["GET_EDGES"], source_serial, dest_serial)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def get_uplink_details(self, conn, source_serial, uplink_id):
        """Get details of an uplink. The serials of node/device on one side of\
        the uplink and the uplink id of the uplink should passed as input.\
Desired uplink id can be found in get
        topology details api.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param source_serial: Device serial number.xx
        :type source_serial: str
        :param uplink_id: Uplink id.
        :type uplink_id: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(
            urls.TOPOLOGY["GET_UPLINK"],
            source_serial,
            str(uplink_id))
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def tunnel_details(self, conn, site_id, tunnel_map_names):
        """Get tunnel details.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_id: Site ID
        :type site_id: int
        :param tunnel_map_names: Comma separated list of tunnel map names.
        :type tunnel_map_names: list
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.TOPOLOGY["GET_TUNNEL"], str(site_id))
        params = {}
        params["tunnel_map_names"] = tunnel_map_names
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def ap_lldp_neighbors(self, conn, device_serial):
        """Get neighbor details reported by AP via LLDP.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serial: Device serial number.
        :type device_serial: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.TOPOLOGY["GET_AP_LLDP"], device_serial)

        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp
