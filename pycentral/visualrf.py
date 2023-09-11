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

from pycentral.url_utils import VisualrfUrl, urlJoin
from pycentral.base_utils import console_logger

urls = VisualrfUrl()


class ClientLocation(object):
    """A python class to obtain client location based on visualRF floor map.
    """

    def get_client_location(self, conn, macaddr: str, offset=0, limit=100,
                            units="FEET"):
        """Get location of a client. This function provides output only when\
            visualRF is configured in Aruba Central.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param macaddr: Provide a macaddr of a client. For example\
            "ac:bb:cc:dd:ec:10"
        :type macaddr: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.CLIENT_LOCATION["GET_CLIENT_LOC"], macaddr)
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_floor_clients(self, conn, floor_id: str, offset=0, limit=100,
                          units="FEET"):
        """Get location of clients within a floormap in Aruba Central visualRF.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param floor_id: Provide floor_id returned by `get_building_floors()`\
            function in class:`FloorPlan`
        :type floor_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(
            urls.CLIENT_LOCATION["GET_FLOOR_CLIENTS"],
            floor_id,
            "client_location")
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp


class RougueLocation(object):
    """A python class to obtain location of rogue access points
    """

    def get_rogueap_location(self, conn, macaddr: str, offset=0, limit=100,
                             units="FEET"):
        """Get location of rogue a access point based on its Mac Address

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
             API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param macaddr: Provide Mac Address of an Access Point
        :type macaddr: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.ROGUE_LOCATION["GET_AP_LOC"], macaddr)
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_floor_rogueaps(self, conn, floor_id: str, offset=0, limit=100,
                           units="FEET"):
        """Get rogue access points within a floor

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param floor_id: Provide floor id. Can be obtained from\
            `get_building_floors()` within class:`FloorPlan`
        :type floor_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.ROGUE_LOCATION["GET_FLOOR_APS"], floor_id)
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp


class FloorPlan(object):
    """A Python class to obtain information of floorplan in Aruba Central\
        visualRF.
    """

    def get_campus_list(self, conn, offset=0, limit=100):
        """Get list of campuses in visualRF floorplan

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.FLOOR_PLAN["GET_CAMPUS_LIST"]
        params = {
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_campus_buildings(self, conn, campus_id: str, offset=0, limit=100):
        """Get campus info and buildings within the campus

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param campus_id: Provide campus id. Can be obtained from\
            `get_campus_list` function in class:`FloorPlan`
        :type campus_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.FLOOR_PLAN["GET_CAMPUS_INFO"], campus_id)
        params = {
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_building_floors(self, conn, building_id: str, offset=0, limit=100,
                            units="FEET"):
        """Get building info and floors within the building

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param building_id: Provide building id. Can be obtained from\
            `get_campus_buildings` within class:`FloorPlan`
        :type building_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.FLOOR_PLAN["GET_BUILDING_INFO"], building_id)
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_floor_info(self, conn, floor_id: str, offset=0, limit=100,
                       units="FEET"):
        """Get floor information

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param floor_id: Provide floor id. Can be obtained from\
            `get_building_floors()` within class:`FloorPlan`
        :type floor_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.FLOOR_PLAN["GET_FLOOR_INFO"], floor_id)
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_floor_image(self, conn, floor_id, offset=0, limit=100):
        """Get Floor's background image in base64 format

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param floor_id: Provide floor id. Can be obtained from\
            `get_building_floors()` within class:`FloorPlan`
        :type floor_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.FLOOR_PLAN["GET_FLOOR_IMG"], floor_id, "image")
        params = {
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_floor_aps(self, conn, floor_id, offset=0, limit=100, units="FEET"):
        """Get access points within a floor

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param floor_id: Provide floor id. Can be obtained from\
            `get_building_floors()` within class:`FloorPlan`
        :type floor_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(
            urls.FLOOR_PLAN["GET_FLOOR_APS"],
            floor_id,
            "access_point_location")
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_ap_location(self, conn, ap_id: str, offset=0, limit=100,
                        units="FEET"):
        """Get location of an access point within a floorplan

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param ap_id: Provide ap_id returned by `get_floor_aps()` within\
            class:`FloorPlan`
        :type ap_id: str
        :param offset: Pagination start index., defaults to 0
        :type offset: int, optional
        :param limit: Pagination size. Default 100 Max 100, defaults to 100
        :type limit: int, optional
        :param units: METERS or FEET, defaults to "FEET"
        :type units: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.FLOOR_PLAN["GET_AP_LOC"], ap_id)
        params = {
            "offset": offset,
            "limit": limit,
            "units": units
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp
