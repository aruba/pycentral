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

import json
import re
import os
import sys
import time
import requests
import errno
from pycentral.base_utils import tokenLocalStoreUtil
from pycentral.base_utils import C_DEFAULT_ARGS, get_url
from pycentral.base_utils import console_logger, parseInputArgs

SUPPORTED_METHODS = ("POST", "PATCH", "DELETE", "GET", "PUT")


class BearerAuth(requests.auth.AuthBase):
    """This class uses Bearer Auth method to generate the authorization header
    from Aruba Central Access Token.

    :param token: Aruba Central Access Token
    :type token: str
    """

    def __init__(self, token):
        """Constructor Method"""
        self.token = token

    def __call__(self, r):
        """Internal method returning auth"""
        r.headers["authorization"] = "Bearer " + self.token
        return r


class ArubaCentralBase:
    """This is the Base class for Aruba Central which handles - \n
    1. token management (OAUTH2.0, cache/storage for reuse and refresh token).\
        Default token caching is in unencrypted file. Override with your\
        implementation for secure handling of access tokens.
    2. command function makes API requests, handles token expiry and\
        auto-refresh expired tokens. Auto-refresh feature is functional only\
        when OAUTH2.0 is provided. Otherwise, refresh expired tokens at your\
        convenience.

    :param central_info: Containing information related Aruba Central and API\
        Gateway for HTTPS connection. \n
        * keyword username: (Optional) Aruba Central username string. Provide\
            for OAUTH2.0 if access token is not provided. \n
        * keyword password: (Optional) Aruba Central password string. Provide\
            for OAUTH2.0 if access token is not provided. \n
        * keyword client_id: (Optional) API Gateway client_id string, Provide\
            for OAUTH2.0 and refresh token API. \n
        * keyword client_secret: (Optional) API Gateway client_secret string,\
            Provide for OAUTH2.0 and refresh token API. \n
        * keyword customer_id: (Optional) API Gateway client_secret string,\
            Provide for OAUTH2.0 and refresh token API. \n
        * keyword base_url: Provide the API Gateway string base FQDN in format\
            `https://<Aruba-Central-API-Gateway-Domain-Name>` You need to \
            provide either a base_url or cluster_name. \n
        * keyword cluster_name: Provide the name of the cluster where the\
            Aruba Central account is provisioned. You need to provide either a\
            base_url or cluster_name. You can find the list of supported\
            clusters in the constants.py file. \n
        * keyword token: (Optional) The token dict is mutually excluive with\
            OAUTH2.0 parameters. token dict should consist of the following\
            key-value pairs - \n
                {"access_token": "xxxx", "refresh_token": "XXYY"}\n
    :type central_info: dict
    :param token_store: Placeholder for future development which provides\
        options to secrely cache and reuse access tokens. defaults to None
    :type token_store: dict, optional
    :param user_retries: Number of times API call should be retried after a\
        rate-limit error HTTP 429 occurs.
    :type user_retries: int, optional
    :param logger: Provide an instance of class:`logging.logger`, defaults to\
        logger class with name "ARUBA_BASE".
    :type logger: class:`logging.logger`, optional
    :param ssl_verify: When set to True, validates SSL certs of Aruba Central\
        API Gateway, defaults to True
    :type ssl_verify: bool, optional
    """

    def __init__(self, central_info, token_store=None, logger=None,
                 ssl_verify=True, user_retries=10):
        """Constructor Method initializes access token. If user provides\
        access token, use the access token for API calls. Otherwise try to\
        reuse token from cache or try to generate new access token via OAUTH\
        2.0. Terminates the program if unable to initialize the access token.
        """
        self.central_info = parseInputArgs(central_info)
        self.token_store = token_store
        self.logger = None
        self.ssl_verify = ssl_verify
        self.user_retries = user_retries
        # Set logger
        if logger:
            self.logger = logger
        else:
            self.logger = console_logger("ARUBA_BASE")
        # Set token
        if "token" in self.central_info and self.central_info["token"]:
            if "access_token" not in self.central_info["token"]:
                self.central_info["token"] = self.getToken()
        else:
            self.central_info["token"] = self.getToken()

        if not self.central_info["token"]:
            sys.exit("exiting.. unable to get API access token!")

    def oauthLogin(self):
        """This function is Step1 of the OAUTH2.0 mechanism to generate access\
            token. Login to Aruba Central
        is performed using username and password.

        :return: Tuple with two strings, csrf token and login session key.
        :rtype: tuple
        """
        headers = {"Content-Type": "application/json"}

        path = "/oauth2/authorize/central/api/login"
        query = {"client_id": self.central_info["client_id"]}
        url = get_url(
            base_url=self.central_info["base_url"], path=path, query=query)

        data = json.dumps(
            {
                "username": self.central_info["username"],
                "password": self.central_info["password"],
            }
        )
        data = data.encode("utf-8")
        try:
            s = requests.Session()
            req = requests.Request(
                method="POST", url=url, data=data, headers=headers)
            prepped = s.prepare_request(req)
            settings = s.merge_environment_settings(
                prepped.url, {}, None, self.ssl_verify, None
            )
            resp = s.send(prepped, **settings)
            if resp and resp.status_code == 200:
                cookies = resp.cookies.get_dict()
                return cookies["csrftoken"], cookies["session"]
            else:
                resp_msg = {
                    "code": resp.status_code,
                    "msg": resp.text
                }
                self.logger.error(
                    "OAUTH2.0 Step1 login API call failed with response "
                    + str(resp_msg)
                )
                sys.exit(1)
        except Exception as e:
            self.logger.error("OAUTH2.0 Step1 failed with error " + str(e))
            sys.exit(1)

    def oauthCode(self, csrf_token, session_token):
        """This function is Step2 of the OAUTH2.0 mechanism to get auth code\
            using CSRF token and session key.

        :param csrf_token: CSRF token obtained from Step1 of OAUTH2.0
        :type csrf_token: str
        :param session_token: Session key obtained from Step1 of OAUTH2.0
        :type session_token: str
        :return: Auth code received in the response payload of the API call.
        :rtype: str
        """
        auth_code = None
        path = "/oauth2/authorize/central/api"
        query = {
            "client_id": self.central_info["client_id"],
            "response_type": "code",
            "scope": "all"
        }
        url = get_url(
            base_url=self.central_info["base_url"], path=path, query=query)

        customer_id = self.central_info["customer_id"]
        data = json.dumps({"customer_id": customer_id}).encode("utf-8")
        headers = {
            "X-CSRF-TOKEN": csrf_token,
            "Content-Type": "application/json",
            "Cookie": "session=" + session_token
        }
        try:
            s = requests.Session()
            req = requests.Request(
                method="POST", url=url, data=data, headers=headers)
            prepped = s.prepare_request(req)
            settings = s.merge_environment_settings(
                prepped.url, {}, None, self.ssl_verify, None
            )
            resp = s.send(prepped, **settings)
            if resp and resp.status_code == 200:
                result = json.loads(resp.text)
                auth_code = result["auth_code"]
                return auth_code
            else:
                resp_msg = {"code": resp.status_code, "msg": resp.text}
                self.logger.error(
                    "OAUTH2.0 Step2 obtaining Auth code API call failed with\
                        response " + str(resp_msg)
                )
                sys.exit(1)
        except Exception as e:
            self.logger.error(
                "Central Login Step2 failed with error " + str(e))
            sys.exit(1)

    def oauthAccessToken(self, auth_code):
        """This function is Step3 of the OAUTH2.0 mechanism to generate API\
            access token.

        :param auth_code: Auth code from Step2 of OAUTH2.0.
        :type auth_code: str
        :return: token information received from API call consisting of\
            access_token and refresh_token.
        :rtype: dict
        """
        path = "/oauth2/token"
        query = {
            "client_id": self.central_info["client_id"],
            "client_secret": self.central_info["client_secret"],
            "grant_type": "authorization_code",
            "code": auth_code
        }
        url = get_url(
            base_url=self.central_info["base_url"], path=path, query=query)

        try:
            s = requests.Session()
            req = requests.Request(method="POST", url=url)
            prepped = s.prepare_request(req)
            settings = s.merge_environment_settings(
                prepped.url, {}, None, self.ssl_verify, None
            )
            resp = s.send(prepped, **settings)
            if resp.status_code == 200:
                result = json.loads(resp.text)
                token = result
                return token
            else:
                resp_msg = {"code": resp.status_code, "msg": resp.text}
                self.logger.error(
                    "OAUTH2.0 Step3 creating access token API call failed with\
                        response "
                    + str(resp_msg)
                )
                sys.exit(1)
        except Exception as e:
            self.logger.error(
                "Central Login Step3 failed with error " + str(e))
            sys.exit(1)

    def validateOauthParams(self):
        """This function validates if all required parameters are available to\
            obtain access_token via OAUTH2.0 mechanism
        in Aruba Central.

        :return: True when validation of availability of the required\
            parameters passed.
        :rtype: bool
        """
        oauth_keys = [
            "client_id",
            "client_secret",
            "customer_id",
            "username",
            "password",
            "base_url",
        ]
        oauth_keys = set(oauth_keys)
        input_keys = set(self.central_info.keys())
        missing_keys = []
        for key in oauth_keys:
            if key not in input_keys:
                missing_keys.append(key)
            if not self.central_info[key]:
                missing_keys.append(key)
        if missing_keys:
            self.logger.error(
                "Missing input parameters " "%s required for OAuth" %
                str(missing_keys)
            )
            return False
        return True

    def validateRefreshTokenParams(self):
        """This function validates if all required parameters are available\
            for refresh token API call.

        :return: True when the validation of the availability of required\
            parameters passed.
        :rtype: bool
        """
        required_keys = ["base_url", "client_id", "client_secret"]
        required_keys = set(required_keys)
        input_keys = set(self.central_info.keys())
        missing_keys = []
        for key in required_keys:
            if key not in input_keys:
                missing_keys.append(key)
            if not self.central_info[key]:
                missing_keys.append(key)
        if missing_keys:
            self.logger.warning(
                "Missing required parameters for refresh "
                "token %s" % str(missing_keys)
            )
            return False
        return True

    def createToken(self):
        """This function generates a new access token for Aruba Central via\
            OAUTH2.0 APIs.

        :return: The token dict conisting of access_token and refresh_token.
        :rtype: dict
        """
        csrf_token = None
        session_token = None
        auth_code = None
        access_token = None
        if not self.validateOauthParams():
            return None
        # Step 1: Login and obtain csrf token and session key
        csrf_token, session_token = self.oauthLogin()
        # Step 2: Obtain Auth Code
        auth_code = self.oauthCode(csrf_token, session_token)
        # Step 3: Swap the auth_code for access token
        access_token = self.oauthAccessToken(auth_code)
        self.logger.info("Central Login Successfull.. Obtained Access Token!")
        return access_token

    def refreshToken(self, old_token):
        """This function refreshes the provided API Gateway token using\
        OAUTH2.0 API. In addition to the input args, this function also\
        depends on the class variable definitions client_id and client_secret.

        :param old_token: API Gateway token dict consisting of refresh_token.
        :type old_token: dict
        :raises UserWarning: Raises warning when validation of availability of\
            the required parameters fails.
        :raises UserWarning: Raises warning when token input param is provided\
            but it doesn't have refresh_token.
        :return: Token dictionary consisting of refreshed access_token and new\
            refresh_token.
        :rtype: dict
        """
        token = None
        resp = ""
        try:
            if not self.validateRefreshTokenParams():
                raise UserWarning("")
            if "refresh_token" not in old_token:
                raise UserWarning(
                    "refresh_token not present in the input " "token dict"
                )

            path = "/oauth2/token"
            query = {
                "client_id": self.central_info["client_id"],
                "client_secret": self.central_info["client_secret"],
                "grant_type": "refresh_token",
                "refresh_token": old_token["refresh_token"],
            }
            url = get_url(
                base_url=self.central_info["base_url"], path=path, query=query
            )

            s = requests.Session()
            req = requests.Request(method="POST", url=url)
            prepped = s.prepare_request(req)
            settings = s.merge_environment_settings(
                prepped.url, {}, None, self.ssl_verify, None
            )
            resp = s.send(prepped, **settings)
            if resp.status_code == 200:
                token = json.loads(resp.text)
            else:
                resp_msg = {"code": resp.status_code, "msg": resp.text}
                self.logger.error(
                    "Refresh token API call failed with response " +
                    str(resp_msg)
                )
        except Exception as err:
            self.logger.error("Unable to refresh token.. " "%s" % str(err))
        return token

    def storeToken(self, token):
        """This function handles storage of token for later use. Default\
        storage is unencrypted JSON file and is not secure. Override this\
        function and loadToken function to implement secure access token\
        caching mechanism.

        :param token: API Gateway token dict consisting of access_token and\
            refresh_token.
        :type token: dict
        :return: True if the access_token caching is successful.
        :rtype: bool
        """
        fullName = tokenLocalStoreUtil(
            self.token_store,
            self.central_info["customer_id"],
            self.central_info["client_id"]
        )
        if not os.path.exists(os.path.dirname(fullName)):
            try:
                os.makedirs(os.path.dirname(fullName))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    self.logger.error(
                        "Storing token failed with error " "%s" % str(exc)
                    )

        # Dumping data to json file
        try:
            with open(fullName, "w") as fp:
                json.dump(token, fp, indent=2)
            self.logger.info(
                "Stored Aruba Central token in file " + "%s" % str(fullName)
            )
            return True
        except Exception as err:
            self.logger.error("Storing token failed with error %s" % str(err))
        return False

    def loadToken(self):
        """This function handles loading API Gateway token from cache/storage.\
        Default token load is from local JSON file. Override this function\
        with storeToken function to implement secure access token caching\
        mechanism.

        :raises UserWarning: Warning to capture empty JSON
        :return: token dict loaded from default implementation of locally\
            stored JSON file consisting of access_token and refresh_token.
        :rtype: dict
        """
        fullName = tokenLocalStoreUtil(
            self.token_store,
            self.central_info["customer_id"],
            self.central_info["client_id"]
        )
        token = None
        try:
            with open(fullName, "r") as fp:
                token = json.load(fp)
            if token:
                self.logger.info(
                    "Loaded token from storage from file: " +
                    "%s" % str(fullName)
                )
            else:
                raise UserWarning("Empty file!")
        except Exception as err:
            self.logger.error(
                "Unable to load token from storage with error " ".. %s" %
                str(err)
            )
        return token

    def handleTokenExpiry(self):
        """This function handles 401 error as a result of HTTP request.\
        An attempt to refresh token is made. If refreshing token fails, this\
        function tries to create new access token. Stores token for reuse. If\
        all the attemps fail, program is terminated.
        """
        self.logger.info("Handling Token Expiry...")
        token = self.refreshToken(self.central_info["token"])
        if token:
            self.logger.info("Expired access token refreshed!")
        else:
            self.logger.info("Attemping to create new token...")
            token = self.createToken()
        if token:
            self.central_info["token"] = token
            self.storeToken(token)
        else:
            self.logger.error("Failed to get API access token")

    def getToken(self):
        """This function attempts to obtain token from storage/cache otherwise\
        creates new access token. Stores the token if new token is generated.

        :return: API Gateway token dict consisting of access_token and\
            refresh_token
        :rtype: dict
        """
        # Check if the token is stored
        token = self.loadToken()
        if token:
            return token
        # Otherwise generate new token
        else:
            self.logger.info(
                "Attempting to create new token from " "Aruba Central")
            token = self.createToken()
            if token and token != "":
                self.storeToken(token)
        if not token:
            self.logger.error("Unable to get API Access Token!")
        return token

    def requestUrl(self, url, data={}, method="GET", headers={}, params={},
                   files={}):
        """This function makes API call to Aruba Central via python requests\
            library.

        :param url: HTTP Request URL string
        :type url: string
        :param data: HTTP Request payload, defaults to {}
        :type data: dict, optional
        :param method: HTTP Request Method supported by Aruba Central,\
            defaults to "GET"
        :type method: str, optional
        :param headers: HTTP Request headers, defaults to {}
        :type headers: dict, optional
        :param params: HTTP url query parameteres, defaults to {}
        :type params: dict, optional
        :param files: files dictionary with file pointer depending on API\
            endpoint as acceped by Aruba Central, defaults to {}
        :type files: dict, optional
        :return: HTTP response of API call using requests library
        :rtype: class:`requests.models.Response`
        """
        resp = None
        if method not in SUPPORTED_METHODS:
            str1 = "HTTP method '%s' not supported.. " % method
            self.logger.error(str1)

        auth = BearerAuth(self.central_info["token"]["access_token"])
        s = requests.Session()
        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            auth=auth,
            params=params,
            data=data,
        )
        prepped = s.prepare_request(req)
        settings = s.merge_environment_settings(
            prepped.url, {}, None, self.ssl_verify, None
        )
        try:
            resp = s.send(prepped, **settings)
            return resp
        except Exception as err:
            str1 = "Failed making request to URL %s " % url
            str2 = "with error %s" % str(err)
            self.logger.error(str1 + str2)

    def command(self, apiMethod, apiPath, apiData={}, apiParams={}, headers={},
                files={}):
        """This function calls requestURL to make an API call to Aruba Central\
            after gathering parameters required for API call. When an API call\
            fails with HTTP 401 error code, the same API call is retried once\
            after an attempt to refresh access token or create new access\
            token is made.

        :param apiMethod: HTTP Method for API call. Should be one of the\
            supported methods for the respective Aruba Central API endpoint.
        :type apiMethod: str
        :param apiPath: Path to the API endpoint as required by API endpoint.\
            Refer Aruba Central API reference swagger documentation.
        :type apiPath: str
        :param apiData: HTTP payload for the API call as required by API\
            endpoint. Refer Aruba Central API reference swagger documentation,\
            defaults to {}
        :type apiData: dict, optional
        :param apiParams: HTTP url query parameters as required by API\
            endpoint. Refer Aruba Central API reference swagger, defaults to {}
        :type apiParams: dict, optional
        :param headers: HTTP headers as required by API endpoint. Refer Aruba\
            Central API reference swagger, defaults to {}
        :type headers: dict, optional
        :param files: Some API endpoints require a file upload instead of\
            apiData. Provide file data in the format accepted by API endpoint\
            and Python requests library, defaults to {}
        :type files: dict, optional
        :return: HTTP response with HTTP status_code and HTTP response\
            payload.\n
            * keyword code: HTTP status code \n
            * keyword msg: HTTP response payload \n
        :rtype: dict
        """
        retry = 0
        result = ""
        method = apiMethod
        limit_reached = False
        self.user_retries
        try:
            while not limit_reached:
                url = get_url(
                    self.central_info["base_url"], apiPath, query=apiParams)
                if not headers and not files:
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                if apiData and headers["Content-Type"] == "application/json":
                    apiData = json.dumps(apiData)

                resp = self.requestUrl(
                    url=url,
                    data=apiData,
                    method=method,
                    headers=headers,
                    params=apiParams,
                    files=files,
                )

                if resp.status_code == 401 and "invalid_token" in resp.text:
                    self.logger.error(
                        "Received error 401 on requesting url "
                        "%s with resp %s" % (str(url), str(resp.text))
                    )

                    if retry >= 1:
                        limit_reached = True
                        break
                    self.handleTokenExpiry()
                    retry += 1

                elif (
                    resp.status_code == 429
                    and resp.headers["X-RateLimit-Remaining-second"] == "0"
                ):
                    time.sleep(2)
                    self.logger.info(
                        "Per-second rate limit reached. Adding 2 seconds \
                            interval and retrying."
                    )
                    if retry == self.user_retries - 1:
                        limit_reached = True
                    retry += 1

                elif (
                    resp.status_code == 429
                    and resp.headers["X-RateLimit-Remaining-day"] == "0"
                ):
                    self.logger.info(
                        "Per-day rate limit of "
                        + str(resp.headers["X-RateLimit-Limit-day"])
                        + " is exhausted. Please check Central UI to see when \
                            the daily rate limit quota will be reset."
                    )
                    limit_reached = True
                else:
                    break

            result = {
                "code": resp.status_code,
                "msg": resp.text,
                "headers": dict(resp.headers),
            }

            try:
                result["msg"] = json.loads(result["msg"])
            except BaseException:
                result["msg"] = str(resp.text)

            return result

        except Exception as err:
            self.logger.error(err)
            exit("exiting...")
