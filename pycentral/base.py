# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from oauthlib.oauth2.rfc6749.errors import InvalidClientError
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
import json
import time
from .utils.base_utils import (
    build_url,
    new_parse_input_args,
    console_logger,
    save_access_token,
)
from .scopes import Scopes
from .exceptions import LoginError, ResponseError
import httpx

SUPPORTED_API_METHODS = ("POST", "PATCH", "DELETE", "GET", "PUT")
MAX_CONNECTIONS = 7
RETRY_MAX_RETRIES = 3
RETRY_INITIAL_BACKOFF = 1.0
RETRY_MAX_BACKOFF = 10.0
RETRY_BACKOFF_MULTIPLIER = 2.0
TRANSIENT_TRANSPORT_ERRORS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.ProxyError,
)


class NewCentralBase:
    def __init__(self, token_info, logger=None, log_level="INFO", enable_scope=False):
        """
        Constructor initializes the NewCentralBase class with token information and logging configuration.

        Validates and processes the provided token information, sets up logging,
        and optionally initializes scope-related functionality.

        Args:
            token_info (dict or str): Dictionary containing token information for supported
                applications (new_central, glp). Can also be a string path to a YAML or
                JSON file with token information.
            logger (logging.Logger, optional): Logger instance. Defaults to None.
            log_level (str, optional): Logging level. Defaults to "INFO".
            enable_scope (bool, optional): Flag to enable scope management. If True, the SDK
                will automatically fetch data about existing scopes and associated profiles,
                simplifying scope and configuration management. If False, scope-related API
                calls are disabled, resulting in faster initialization. Defaults to False.
        """
        self.token_info = new_parse_input_args(token_info)
        self.token_file_path = None
        if isinstance(token_info, str):
            self.token_file_path = token_info
        self.logger = self.set_logger(log_level, logger)
        self._app_routes = self._build_app_routes()
        self.scopes = None
        self._http_clients = {}
        self._initialize_http_clients()
        self._initialize_tokens()
        if enable_scope:
            self.scopes = Scopes(central_conn=self)

    def set_logger(self, log_level, logger=None):
        """
        Set up the logger.

        Args:
            log_level (str): Logging level.
            logger (logging.Logger, optional): Logger instance. Defaults to None.

        Returns:
            (logging.Logger): Logger instance.
        """
        if logger:
            return logger
        else:
            return console_logger("NEW CENTRAL BASE", log_level)

    def _build_app_routes(self):
        """
        Build a per-app routing table from token_info, computed once at init.

        Maps each caller-facing app name ('glp', 'new_central') to its
        base_url and the token_info key holding the access token.

        Returns:
            (dict): Mapping of app_name to {"base_url": str, "token_key": str}.

        Note:
            Internal SDK function
        """
        routes = {}
        if "unified" in self.token_info:
            unified = self.token_info["unified"]
            routes["glp"] = {
                "base_url": unified["glp_base_url"],
                "token_key": "unified",
            }
            if unified.get("base_url"):
                routes["new_central"] = {
                    "base_url": unified["base_url"],
                    "token_key": "unified",
                }
        else:
            for app_name, app_info in self.token_info.items():
                routes[app_name] = {
                    "base_url": app_info["base_url"],
                    "token_key": app_name,
                }
        return routes

    def _initialize_http_clients(self):
        """Create HTTP clients for every app in the routing table."""
        for app_name in self._app_routes:
            self._http_clients[app_name] = self._create_http_client(app_name)
        if "unified" in self.token_info and "new_central" not in self._app_routes:
            self.logger.info(
                "Unified mode: no 'base_url' or 'cluster_name' was provided for "
                "Central. Only GLP API calls are supported. Add 'base_url' or "
                "'cluster_name' under 'unified' credentials to also enable Central calls."
            )

    def _initialize_tokens(self):
        """Fetch an access token for any app that does not already have one."""
        for app in list(self.token_info):
            app_token_info = self.token_info[app]
            if (
                "access_token" not in app_token_info
                or app_token_info["access_token"] is None
            ):
                self.create_token(app)

    def _create_http_client(self, app_name):
        """
        Create an HTTP client for a specific app.

        Uses tuned connection limits for New Central and default connection
        limits for all other apps (including GLP).

        Args:
            app_name (str): Name of the application (e.g., "new_central", "glp").

        Returns:
            (httpx.Client): Configured HTTP client instance.

        Note:
            Internal SDK function
        """
        client_kwargs = {
            "http2": True,
            "timeout": httpx.Timeout(30.0, connect=10.0),
            "verify": True,
        }
        # Apply tuned connection limits for Central requests
        # (both standalone new_central and the unified platform client for Central)
        if app_name in ("new_central",):
            client_kwargs["limits"] = httpx.Limits(
                max_connections=MAX_CONNECTIONS,
                max_keepalive_connections=5,
                keepalive_expiry=30,
            )
        return httpx.Client(**client_kwargs)

    def create_token(self, app_name):
        """
        Create a new access token for the specified application.

        Generates a new access token using the client credentials for the specified
        application, updates the self.token_info dictionary with the new token,
        and optionally saves it to a file.

        Args:
            app_name (str): Name of the application. Supported applications: "new_central", "glp".

        Returns:
            (str): Access token.

        Raises:
            LoginError: If there is an error during token creation.
        """
        client_id, client_secret = self._return_client_credentials(app_name)
        client = BackendApplicationClient(client_id)

        oauth = OAuth2Session(client=client)
        auth = HTTPBasicAuth(client_id, client_secret)

        token_url = self.token_info[app_name].get("_token_url")
        if not token_url:
            raise ValueError(
                f"Cannot determine token URL for '{app_name}'. "
                "Ensure valid credentials (including workspace_id for unified mode) are provided."
            )

        try:
            self.logger.info(f"Attempting to create new token from {app_name}")
            token = oauth.fetch_token(token_url=token_url, auth=auth)
            if "access_token" not in token:
                msg = (
                    f"Token response for '{app_name}' did not contain an access_token. "
                    "Verify that the client credentials and token URL are correct."
                )
                self.logger.error(msg)
                raise LoginError(msg)
            self.logger.info(
                f"{app_name} Login Successful.. Obtained Access Token!"
            )
            self.token_info[app_name]["access_token"] = token["access_token"]
            if self.token_file_path:
                save_access_token(
                    app_name,
                    token["access_token"],
                    self.token_file_path,
                    self.logger,
                )
            return token["access_token"]
        except Exception as e:
            # unified extraction of status code (from exception or its response)
            status_code = getattr(e, "status_code", None)
            resp = getattr(e, "response", None)
            if resp is not None:
                status_code = getattr(resp, "status_code", status_code)

            # special-case invalid client credentials to provide a clearer, actionable message
            if isinstance(e, InvalidClientError):
                description = getattr(e, "description", None) or str(e)
                msg = (
                    f"{description} for {app_name}. "
                    "Provide valid client_id and client_secret to create an access token."
                )
            else:
                msg = str(e) or "Unexpected error while creating access token"

            self.logger.error(msg)
            raise LoginError(msg, status_code)

    def command(
        self,
        api_method,
        api_path,
        app_name="new_central",
        api_data=None,
        api_params=None,
        headers=None,
        files=None,
    ):
        """
        Execute an API command to Central or GreenLake Platform.

        This is the primary method for making API calls from the SDK. It handles
        authentication, token refresh on expiry, request formatting, and response
        parsing. All other SDK modules internally use this method to make API calls.

        The method automatically:
            - Validates the application name and HTTP method
            - Constructs the full URL from self.base_url and api_path
            - Adds appropriate headers (Content-Type, Accept) if not provided
            - Serializes api_data to JSON when Content-Type is application/json
            - Handles 401 errors by refreshing the access token and retrying if client credentials are available
            - Parses JSON responses when possible

        Args:
            api_method (str): HTTP method for the API call. Supported methods:
                POST, PATCH, DELETE, GET, PUT.
            api_path (str): API endpoint path (e.g., "monitoring/v1/aps").
                This is appended to the base_url configured in token_info.
            app_name (str, optional): Target application for the API call.
                Use "new_central" for Central APIs (default).
                Use "glp" for GreenLake Platform APIs.
            api_data (dict, optional): Request body/payload to be sent. Automatically
                serialized to JSON if Content-Type is application/json. Defaults to None.
            api_params (dict, optional): URL query parameters for the API request.
                Defaults to None.
            headers (dict, optional): Custom HTTP headers. If not provided and no files
                are being uploaded, defaults to {"Content-Type": "application/json",
                "Accept": "application/json"}.
            files (dict, optional): Files to upload in multipart/form-data requests.
                When provided, Content-Type header is not automatically set. Defaults to None.

        Returns:
            (dict): API response containing:
                - code (int): HTTP status code
                - msg (dict or str): Parsed JSON response body, or raw text if not JSON
                - headers (dict): Response headers

        Raises:
            ResponseError: If there is an error during the API call.
        """
        self._validate_request(app_name, api_method)

        api_data = api_data if api_data is not None else {}
        files = files if files is not None else {}

        api_params = self._prepare_query_params(api_params)
        req_headers = self._build_request_headers(headers, files)
        req_data = self._serialize_request_data(api_data, req_headers)

        route = self._app_routes[app_name]
        url = build_url(route["base_url"], api_path)

        retry = 0
        resp = None
        limit_reached = False
        try:
            while not limit_reached:
                resp = self.request_url(
                    url=url,
                    data=req_data,
                    method=api_method,
                    headers=req_headers,
                    params=api_params,
                    files=files,
                    access_token=self.token_info[route["token_key"]]["access_token"],
                    app_name=app_name,
                )
                if resp.status_code == 401:
                    if retry >= 1:
                        self.logger.error(
                            "Received error 401 on requesting url "
                            "%s with resp %s" % (str(url), str(resp.text))
                        )
                        limit_reached = True
                        break
                    self.logger.info(
                        f"{app_name} access token has expired. Handling Token Expiry..."
                    )
                    self._renew_token(route["token_key"])
                    retry += 1
                else:
                    break

            if resp is None:
                raise ResponseError(
                    f"{api_method} FAILURE ",
                    RuntimeError(f"No response returned for {api_method} {url}"),
                )

            result = {
                "code": resp.status_code,
                "msg": resp.text,
                "headers": dict(resp.headers),
            }

            try:
                result["msg"] = resp.json()
            except (ValueError, json.JSONDecodeError):
                result["msg"] = resp.text

            return result

        except (LoginError, ValueError):
            raise
        except Exception as err:
            err_str = f"{api_method} FAILURE "
            self.logger.error(err)
            raise ResponseError(err_str, err)

    def _prepare_query_params(self, api_params):
        """
        Return query params with None-valued entries removed.

        Args:
            api_params (dict or None): Query parameters to filter.

        Returns:
            (dict): Query parameters with None values removed.

        Note:
            Internal SDK function
        """
        if api_params is None:
            return {}
        if isinstance(api_params, dict):
            return {
                key: value for key, value in api_params.items() if value is not None
            }
        return api_params

    def _build_request_headers(self, headers, files):
        """
        Build request headers without mutating caller-provided headers.

        Args:
            headers (dict or None): Custom HTTP headers provided by the caller.
            files (dict): Files dictionary for multipart upload requests.

        Returns:
            (dict): Request headers to use for the API call.

        Note:
            Internal SDK function
        """
        if headers:
            return dict(headers)
        if not files:
            return {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        return {}

    def _serialize_request_data(self, api_data, req_headers):
        """
        Serialize payload for JSON requests; otherwise pass through as-is.

        Args:
            api_data (dict or str or bytes): Request payload data.
            req_headers (dict): Request headers (used to detect Content-Type).

        Returns:
            (str or dict or bytes): Serialized request data.

        Note:
            Internal SDK function
        """
        content_type = next(
            (
                header_value
                for header_key, header_value in req_headers.items()
                if header_key.lower() == "content-type"
            ),
            "",
        )
        if (
            api_data
            and "application/json" in str(content_type).lower()
            and not isinstance(api_data, (str, bytes, bytearray))
        ):
            return json.dumps(api_data)
        return api_data

    def request_url(
        self,
        url,
        access_token,
        app_name="new_central",
        data=None,
        method="GET",
        headers=None,
        params=None,
        files=None,
    ):
        """Make an API call to application (New Central or GLP) via the requests library.

        Args:
            url (str): HTTP Request URL string.
            access_token (str): Access token for authentication.
            app_name (str, optional): App name used to select HTTP client.
                Defaults to "new_central".
            data (dict, optional): HTTP Request payload. Defaults to None.
            method (str, optional): HTTP Request Method supported by GLP/New Central.
                Defaults to "GET".
            headers (dict, optional): HTTP Request headers. Defaults to None.
            params (dict, optional): HTTP URL query parameters. Defaults to None.
            files (dict, optional): Files dictionary with file pointer depending on
                API endpoint as accepted by GLP/New Central. Defaults to None.

        Returns:
            (requests.models.Response): HTTP response of API call using requests library.

        Raises:
            ResponseError: If there is an error during the API call.

        Note:
            Transient transport failures (DNS resolution errors, connection failures,
            timeouts, and proxy errors) are automatically retried with exponential
            backoff up to ``RETRY_MAX_RETRIES`` attempts. All other exceptions are
            raised immediately as ``ResponseError`` without retrying.
        """
        req_headers = dict(headers) if headers else {}
        req_headers["authorization"] = "Bearer " + access_token

        # Build keyword args — httpx does not allow content + data + files together
        kwargs = {
            "method": method,
            "url": url,
            "headers": req_headers,
        }
        if params:
            kwargs["params"] = params
        if files:
            # Multipart upload: use files + optional form data (dict only)
            kwargs["files"] = files
            if data and isinstance(data, dict):
                kwargs["data"] = data
        elif isinstance(data, str):
            # Pre-serialized JSON string — pass directly, httpx handles encoding
            kwargs["content"] = data
        elif isinstance(data, bytes):
            # Raw bytes
            kwargs["content"] = data
        elif isinstance(data, dict) and data:
            # Form-encoded dict
            kwargs["data"] = data

        http_client = self._http_clients.get(app_name)
        if http_client is None:
            http_client = self._create_http_client(app_name)
            self._http_clients[app_name] = http_client

        retry_count = 0
        while True:
            try:
                return http_client.request(**kwargs)
            except TRANSIENT_TRANSPORT_ERRORS as err:
                if retry_count >= RETRY_MAX_RETRIES:
                    err_str = f"Failed making request to URL {url} with error {err}"
                    self.logger.error(err_str)
                    raise ResponseError(err_str, err)
                retry_count += 1
                delay = min(
                    RETRY_INITIAL_BACKOFF * (RETRY_BACKOFF_MULTIPLIER ** (retry_count - 1)),
                    RETRY_MAX_BACKOFF,
                )
                self.logger.warning(
                    "Transient transport failure on %s %s for app %s "
                    "(retry %s/%s): %s. Retrying in %.1f seconds.",
                    method, url, app_name, retry_count, RETRY_MAX_RETRIES, err, delay,
                )
                time.sleep(delay)
            except Exception as err:
                err_str = f"Failed making request to URL {url} with error {err}"
                self.logger.error(err_str)
                raise ResponseError(err_str, err)

    def _renew_token(self, token_key):
        """Renew the access token for the given token_info key.

        Subclasses (e.g. TenantBase) override this to implement
        custom renewal strategies such as MSP tenant token exchange.

        Args:
            token_key (str): Key in self.token_info whose token should be renewed.
        """
        self.create_token(token_key)

    def _validate_request(self, app_name, method):
        """
        Validate that the provided app name is configured and the HTTP method is supported.

        Args:
            app_name (str): Name of the application.
            method (str): HTTP method to be validated.

        Raises:
            ValueError: If app_name is not in token_info or access_token is missing.
            ValueError: If the method is not supported.
        """
        if app_name not in self._app_routes:
            error_string = (
                f"Missing configuration for '{app_name}'. Please provide access token "
                f"or client credentials to generate an access token for app - {app_name}"
            )
            self.logger.error(error_string)
            raise ValueError(error_string)

        if method not in SUPPORTED_API_METHODS:
            error_string = (
                f"HTTP method '{method}' not supported. Please provide an API with one of the "
                f"supported methods - {', '.join(SUPPORTED_API_METHODS)}"
            )
            self.logger.error(error_string)
            raise ValueError(error_string)

    def _return_client_credentials(self, app_name):
        """
        Return client credentials for the specified application.

        Args:
            app_name (str): Name of the application.

        Returns:
            (tuple): Client ID and client secret as a tuple (client_id, client_secret).
        """
        app_token_info = self.token_info[app_name]
        if all(
            client_key in app_token_info
            for client_key in ("client_id", "client_secret")
        ) and app_token_info["client_id"] and app_token_info["client_secret"]:
            client_id = app_token_info["client_id"]
            client_secret = app_token_info["client_secret"]
            return client_id, client_secret
        raise ValueError(
            f"Missing 'client_id' or 'client_secret' for app '{app_name}'. "
            "Provide valid client credentials to create an access token."
        )

    def get_scopes(self):
        """
        Set up the scopes for the current instance by creating a Scopes object.

        Initializes the scopes attribute using the Scopes class, passing the
        current instance as the central_conn parameter. If the scopes attribute
        is already initialized, it simply returns the existing object.

        Returns:
            (Scopes): The initialized or existing Scopes object.
        """
        if self.scopes is None:
            self.scopes = Scopes(central_conn=self)
        return self.scopes

    def close(self):
        """Close all underlying HTTP clients and release connection pool resources."""
        for app_name, http_client in self._http_clients.items():
            try:
                if http_client:
                    http_client.close()
            except Exception as err:
                self.logger.error(f"Failed closing HTTP client for {app_name}: {err}")

        self._http_clients = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Closing HTTP client and releasing resources...")
        self.close()

    # Garbage collection fallback — close if user forgets
    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
