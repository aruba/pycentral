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

from pycentral.url_utils import RefreshUrl
from pycentral.base_utils import console_logger

urls = RefreshUrl()


class RefreshApiToken(object):
    """Refresh the API access token in API Gateway using OAUTH API
    """

    def refresh_token(self, conn, apigw_client_id, apigw_client_secret,
                      old_refresh_token):
        """This function refreshes the existing access token and replaces old\
        token with new token. The returned token dict will contain both access\
        and refresh token. Use refresh token provided in the return dict for\
        next refresh.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param apigw_client_id: Client ID from API Gateway page
        :type apigw_client_id: str
        :param apigw_client_secret: Client Secret from API Gateway page
        :type apigw_client_secret: str
        :param old_refresh_token: Refresh token value from the current/expired\
            API token.
        :type old_refresh_token: str
        :return: Refrehed token dict consisting of access_token and\
            refresh_token.
        :rtype: dict
        """
        path = urls.REFRESH_TOKEN["REFRESH"]
        resp = None
        params = {
            "client_id": apigw_client_id,
            "client_secret": apigw_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": old_refresh_token
        }
        resp = conn.command(
            apiMethod="POST",
            apiPath=path,
            apiParams=params,
            retry_api_call=False)
        return resp
