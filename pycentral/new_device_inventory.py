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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
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
    """A python class consisting of functions to manage Aruba Central Devices via REST API
    """

    def get_inventory(self, conn, sku_type="all", limit=0, offset=0):
        """Get devices from inventory.
        
        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param sku_type: target device type to pull from inventory.  Acceptable arguments: 
            all, iap, switch, controller, gateway, vgw, cap, boc, all_ap, all_controller, others  
        :type sku_type: str
        :param offset: Pagination offset, defaults to 0.  Not currently Implemented.
        :type offset: int, optional
        :param limit: Pagination limit with Max 20, defaults to 20.  Not currently Implemented.
        :type limit: int, optional

        :return: HTTP Response as provided by 'command' function in class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """

        path = urls.DEVICES["GET_DEVICES"]
        params = {
            "limit" : limit,
            "offset" : offset,
            "sku_type" : sku_type
        }

        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp