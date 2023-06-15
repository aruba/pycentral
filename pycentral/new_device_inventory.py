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

from pycentral.url_utils import InventoryUrl

urls = InventoryUrl()


class Inventory(object):
    """
    A python class consisting of functions to manage Aruba Central inventory
    from the new device inventory category via REST API.
    """

    def get_inventory(self, conn, sku_type="all", limit=0, offset=0):
        """Get device details from inventory.

        :param conn: Instance of class:`pycentral.ArubaCentralBase`.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param sku_type: target device sku type to pull from inventory.
            Acceptable arguments: all, iap, switch, controller, gateway,
            vgw, cap, boc, all_ap, all_controller, others.
        :type sku_type: str
        :param limit: Pagination limit. Defaults to 0, which is intrepreted as
            get all. Maximum limit per request is 50.
        :type limit: int, optional
        :param offset: Pagination offset, defaults to 0.
        :type offset: int, optional

        :return: HTTP Response as provided by 'command' function in
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """

        path = urls.DEVICES["GET_DEVICES"]

        # Check limit for default.
        if limit != 0:
            params = {
                "limit": limit,
                "offset": offset,
                "sku_type": sku_type
            }
        else:
            # No limit param to allow get all devices.
            params = {
                "offset": offset,
                "sku_type": sku_type
            }

        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp
