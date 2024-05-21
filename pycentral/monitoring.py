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

import sys
from pycentral.url_utils import urlJoin, MonitoringUrl
from pycentral.base_utils import console_logger

urls = MonitoringUrl()
logger = console_logger("MONITORING")


class Sites(object):
    """A python class consisting of functions to manage Aruba Central Sites\
        via REST API
    """

    def get_sites(self, conn, calculate_total=False, offset=0, limit=100,
                  sort="+site_name"):
        """Get list of sites

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param calculate_total: Whether to calculate total number of sites,\
            defaults to False
        :type calculate_total: bool, optional
        :param offset: Pagination offset, defaults to 0
        :type offset: int, optional
        :param limit: Pagination limit with Max 1000, defaults to 100
        :type limit: int, optional
        :param sort: Sort list of sites based on one of '+site_name',\
            '-site_name', defaults to "+site_name"
        :type sort: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SITES["GET_ALL"]
        params = {
            "offset": offset,
            "limit": limit,
            "calculate_total": calculate_total,
            "sort": sort
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def create_site(self, conn, site_name, site_address={}, geolocation={}):
        """Creates a new site

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_name: Name of the site be created.
        :type site_name: str
        :param site_address: Address of the site, defaults to {} \n
            * keyword address: Site address string \n
            * keyword city: City name string \n
            * keyword state: State name string \n
            * keyword country: Country name string \n
            * keyword zipcode: Zipcode string \n
        :type site_address: dict, optional
        :param geolocation: Mutually exclusive with site address. Provide\
            either one option, defaults to {} \n
            * keyword latitude: Site location latitude in the world map \n
            * keyword longitude: Site location longitude in the world map \n
        :type geolocation: dict, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SITES["CREATE"]
        if not site_address and not geolocation:
            logger.error(
                "Site {} Creation Error.. \
                    Pass Address OR Geolocation!".format(site_name))
            return None

        if site_address and geolocation:
            logger.error(
                "Site {} Creation Error.. Pass Address OR Geolocation,\
                    Not Both!".format(site_name))
            return None

        data = self._build_site_payload(
            site_name=site_name,
            site_address=site_address,
            geolocation=geolocation)
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def update_site(self, conn, site_id, site_name, site_address={},
                    geolocation={}):
        """Update/Modify an existing site

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_id: ID assigned by Aruba Central when the site is created.\
            Can be obtained from find_site_id function.
        :type site_id: int
        :param site_name: Name of the site be created.
        :type site_name: str
        :param site_address: Address of the site, defaults to {} \n
            * keyword address: Site address string \n
            * keyword city: City name string \n
            * keyword state: State name string \n
            * keyword country: Country name string \n
            * keyword zipcode: Zipcode string \n
        :type site_address: dict, optional
        :param geolocation: Mutually exclusive with site address. Provide\
            either one option, defaults to {} \n
            * keyword latitude: Site location latitude in the world map \n
            * keyword longitude: Site location longitude in the world map \n
        :type geolocation: dict, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.SITES["UPDATE"], str(site_id))
        if not site_address and not geolocation:
            logger.error(
                "Site {} Update Error.. \
                    Pass Address OR Geolocation!".format(site_name))
            return None

        if site_address and geolocation:
            logger.error(
                "Site {} Update Error.. Pass Address OR Geolocation, \
                    Not Both!".format(site_name))
            return None

        data = self._build_site_payload(
            site_name=site_name,
            site_address=site_address,
            geolocation=geolocation)
        resp = conn.command(apiMethod="PATCH", apiPath=path, apiData=data)
        return resp

    def delete_site(self, conn, site_id):
        """Delete an existing site

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_id: ID assigned by Aruba Central when the site is created.\
            Can be obtained from find_site_id function.
        :type site_id: int
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.SITES["DELETE"], str(site_id))
        resp = conn.command(apiMethod="DELETE", apiPath=path)
        return resp

    def associate_devices(self, conn, site_id, device_type, device_ids):
        """Associate multiple devices to a site

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_id: ID assigned by Aruba Central when the site is created.\
            Can be obtained from find_site_id function.
        :type site_id: int
        :param device_type: Type of the device. One of the "IAP",\
            "ArubaSwitch", "CX", "MobilityController".
        :type device_type: str
        :param device_ids: List of Aruba devices' serial number
        :type device_ids: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SITES["ADD_DEVICES"]
        if isinstance(device_ids, str):
            device_ids = [device_ids]
        data = self._build_site_devices_payload(
            site_id=site_id, device_type=device_type, device_ids=device_ids)
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def unassociate_devices(self, conn, site_id, device_type, device_ids):
        """Unassociate a device from a site

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_id: ID assigned by Aruba Central when the site is created.\
            Can be obtained
            from find_site_id function.
        :type site_id: int
        :param device_type: Type of the device. One of the "IAP",\
            "ArubaSwitch", "CX", "MobilityController".
        :type device_type: str
        :param device_id: Aruba device serial number
        :type device_id: str
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SITES["DELETE_DEVICES"]
        if isinstance(device_ids, str):
            device_ids = [device_ids]
        data = self._build_site_devices_payload(
            site_id=site_id, device_type=device_type, device_ids=device_ids)
        resp = conn.command(apiMethod="DELETE", apiPath=path, apiData=data)
        return resp

    def find_site_id(self, conn, site_name):
        """Find site id from site name

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param site_name: Name of the site be created.
        :type site_name: str
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        max_limit_size = 1000
        total_count = 0
        pagination_check = True
        offset = 0
        count = 0

        while pagination_check:
            resp = self.get_sites(conn, offset=offset, limit=max_limit_size)
            if resp and "msg" in resp and "sites" in resp["msg"]:
                resp = resp["msg"]
                count = resp["count"]
                total_count = total_count + count
                offset = offset + count

                if total_count == resp["total"]:
                    pagination_check = False

                for site in resp["sites"]:
                    if site["site_name"] == site_name:
                        return site["site_id"]

        return None

    def _build_site_payload(self, site_name, site_address, geolocation):
        """Build HTTP payload for site config

        :param site_name: Name of the site be created.
        :type site_name: str
        :param site_address: Address of the site, defaults to {} \n
            * keyword address: Site address string \n
            * keyword city: City name string \n
            * keyword state: State name string \n
            * keyword country: Country name string \n
            * keyword zipcode: Zipcode string \n
        :type site_address: dict, optional
        :param geolocation: Mutually exclusive with site address. Provide\
            either one option, defaults to {} \n
            * keyword latitude: Site location latitude in the world map \n
            * keyword longitude: Site location longitude in the world map \n
        :type geolocation: dict, optional
        :return: HTTP payload for site config
        :rtype: dict
        """
        payload_json = {
            "site_name": site_name
        }
        if site_address:
            payload_json["site_address"] = site_address
        elif geolocation:
            payload_json["geolocation"] = geolocation
        return payload_json

    def _build_site_devices_payload(self, site_id, device_type, device_ids):
        """HTTP payload for device(s) in a site

        :param site_id: ID assigned by Aruba Central when the site is created.\
            Can be obtained
            from find_site_id function.
        :type site_id: int
        :param device_type: Type of the device. One of the "IAP",\
            "ArubaSwitch", "CX", "MobilityController".
        :type device_type: str
        :param device_ids: List of Aruba devices' serial number
        :type device_ids: list
        :return: HTTP payload for devices in a site
        :rtype: dict
        """
        payload_json = {
            "site_id": site_id,
            "device_type": device_type,
            "device_ids": device_ids
        }
        return payload_json
