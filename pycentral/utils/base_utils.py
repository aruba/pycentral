# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

import logging
import warnings
import yaml
import json
import os
from urllib.parse import urlencode, urlparse, urlunparse
from .constants import AUTHENTICATION, CLUSTER_BASE_URLS, GLP_URLS
from .common_utils import parse_input_file

try:
    import colorlog  # type: ignore

    COLOR = True
except (ImportError, ModuleNotFoundError):
    COLOR = False
SUPPORTED_APPS = ["new_central", "glp", "unified"]
NEW_CENTRAL_C_DEFAULT_ARGS = {
    "base_url": None,
    "client_id": None,
    "client_secret": None,
    "access_token": None,
}
UNIFIED_DEFAULT_ARGS = {
    "client_id": None,
    "client_secret": None,
    "workspace_id": None,
    "glp_base_url": None,
    "base_url": None,
    "access_token": None,
}

APP_TOKEN_CREATION_REQUIRED_KEYS = {
    "new_central": {"client_id", "client_secret"},
    "glp": {"client_id", "client_secret"},
    "unified": {"client_id", "client_secret", "workspace_id"},
}

URL_BASE_ERR_MESSAGE = (
    "Please provide the base_url of API Gateway where Central account is provisioned!"
)

def new_parse_input_args(token_info):
    """
    Parse and validate the input token information.

    Args:
        token_info (dict or str): Dictionary containing token information or a file path
            to a YAML/JSON file with token information.

    Returns:
        (dict): Parsed token information for supported applications.

    Raises:
        ValueError: If the token_info is invalid.

    Note:
        When "unified" credentials are present, any "glp" or "new_central" entries
        in the same dict are ignored. Unified mode requires client credentials
        (`client_id`, `client_secret`, and `workspace_id`). An optional
        `access_token` can be provided to skip initial token creation; the
        client credentials are still required for token refresh when the
        access token expires. Pass `base_url` or `cluster_name` under
        `unified` to also enable Central API calls.
    """
    token_info = load_token_info(token_info)

    if not token_info:
        raise ValueError(
            f"No valid token information provided. Supported apps: {', '.join(SUPPORTED_APPS)}"
        )

    apps_token_info = {}

    # Unified credentials supersede standalone glp/new_central — warn then discard them
    if "unified" in token_info:
        overridden = [k for k in token_info if k in ("glp", "new_central")]
        if overridden:

            warnings.warn(
                f"'unified' credentials were provided alongside {overridden}. "
                f"The {overridden} entries will be ignored; 'unified' takes precedence.",
                UserWarning,
                stacklevel=3,
            )

        unified = dict(token_info["unified"])

        # GLP is always the primary endpoint
        unified["glp_base_url"] = valid_url(
            unified.get("glp_base_url", GLP_URLS["BaseURL"])
        )

        _validate_token_creation_keys("unified", unified)

        unified["base_url"] = _resolve_base_url("unified", unified)
        unified.pop("cluster_name", None)

        # Precompute token URL for token creation/refresh
        if unified.get("workspace_id"):
            unified["_token_url"] = (
                f"{AUTHENTICATION['OAUTH_GLOBAL']}/{unified['workspace_id']}/token"
            )

        apps_token_info["unified"] = {**UNIFIED_DEFAULT_ARGS, **unified}

    else:
        for app, app_token_info in token_info.items():
            if app not in SUPPORTED_APPS:
                raise ValueError(
                    f"Unknown app name '{app}' provided. Supported apps: {', '.join(SUPPORTED_APPS)}"
                )

            app_token_info["base_url"] = _resolve_base_url(app, app_token_info)
            _validate_token_creation_keys(app, app_token_info)
            app_token_info["_token_url"] = AUTHENTICATION["OAUTH"]
            apps_token_info[app] = {**NEW_CENTRAL_C_DEFAULT_ARGS, **app_token_info}

    return apps_token_info


def load_token_info(token_info):
    """
    Load token information from a file if it's a string path, or return the dictionary as is.

    Args:
        token_info (dict or str): Either a dictionary containing token information or a
            string path to a YAML/JSON file with token information.

    Returns:
        (dict): Parsed token information dictionary.

    Raises:
        ValueError: If the file format is unsupported or the file cannot be parsed.
        FileNotFoundError: If the specified file path does not exist.
    """
    if isinstance(token_info, str):
        try:
            token_info = parse_input_file(token_info)
        except (ValueError, FileNotFoundError) as e:
            # Re-raise the exception with additional context
            raise type(e)(f"Failed to load token information: {e}") from e
    return token_info


def _resolve_central_base_url(app, app_token_info, required=True):
    """Resolve a Central base_url from cluster_name or base_url for the given app."""
    if "cluster_name" in app_token_info and "base_url" in app_token_info:
        raise ValueError(
            f"You cannot provide both 'cluster_name' and 'base_url' for {app}. Please provide only one."
        )
    if "cluster_name" in app_token_info:
        cluster_name = app_token_info["cluster_name"]
        if cluster_name in CLUSTER_BASE_URLS:
            return CLUSTER_BASE_URLS[cluster_name]
        raise ValueError(
            f"Invalid cluster_name '{cluster_name}' provided. Supported clusters: {', '.join(CLUSTER_BASE_URLS.keys())}"
        )
    if "base_url" in app_token_info:
        return valid_url(app_token_info["base_url"])
    if required:
        raise ValueError(
            f"For {app}, either 'cluster_name' or 'base_url' must be provided."
        )
    return None


def _resolve_base_url(app, app_token_info):
    """
    Resolve the base_url using cluster_name or validate the provided base_url.

    Args:
        app (str): Name of the application (e.g., "new_central", "glp", "unified").
        app_token_info (dict): Token information for a specific app.

    Returns:
        (str): Validated or resolved base_url, or None if optional and not provided.

    Raises:
        ValueError: If both cluster_name and base_url are provided or a required one is missing.
    """
    if app == "new_central":
        return _resolve_central_base_url(app, app_token_info, required=True)
    elif app == "glp":
        if "base_url" not in app_token_info:
            app_token_info["base_url"] = GLP_URLS["BaseURL"]
        return valid_url(app_token_info["base_url"])
    elif app == "unified":
        return _resolve_central_base_url(app, app_token_info, required=False)
    else:
        raise ValueError(
            f"_resolve_base_url does not handle '{app}' directly. "
            "Only 'new_central', 'glp', and 'unified' are valid inputs."
        )


def _validate_token_creation_keys(app, app_token_info):
    """
    Validate that the required keys for token creation are present.

    Args:
        app (str): Name of the application (e.g., "new_central", "glp", "unified").
        app_token_info (dict): Token information for a specific app.

    Raises:
        ValueError: If required keys are missing or invalid keys are provided.

    Note:
        Internal SDK function
    """
    # For unified mode, client credentials and workspace_id are always
    # required because they are needed for token refresh even when an
    # existing access_token is supplied.
    if app == "unified" or "access_token" not in app_token_info:
        required_keys = APP_TOKEN_CREATION_REQUIRED_KEYS[app]
        missing_keys = required_keys - app_token_info.keys()
        if missing_keys:
            raise ValueError(
                f"Missing required keys for token creation for '{app}': {', '.join(missing_keys)}. "
                "Provide either a valid access token or the required credentials to generate an access token."
            )
    if "access_token" in app_token_info and not isinstance(
        app_token_info["access_token"], str
    ):
        raise ValueError(
            f"'access_token' for '{app}' must be a string. Got {type(app_token_info['access_token']).__name__} instead."
        )


def build_url(base_url, path="", params="", query=None, fragment=""):
    """
    Construct a complete URL based on multiple parts of the URL.

    Args:
        base_url (str): Base URL for an HTTP request.
        path (str, optional): API endpoint path.
        params (str, optional): API endpoint path parameters.
        query (dict, optional): HTTP request URL query parameters.
        fragment (str, optional): URL fragment identifier.

    Returns:
        (str): Parsed URL.
    """
    base_url = valid_url(base_url)
    parsed_baseurl = urlparse(base_url)
    scheme = parsed_baseurl.scheme
    netloc = parsed_baseurl.netloc

    query = query or {}
    query = urlencode(query)
    url = urlunparse((scheme, netloc, path, params, query, fragment))
    return url


def console_logger(name, level="DEBUG"):
    """
    Create an instance of python logging with a formatted output.

    Sets the following format for log messages: `<date> <time> - <name> - <level> - <message>`

    Args:
        name (str): String displayed after date and time. Define it to identify
            from which part of the code the log message is generated.
        level (str, optional): Logging level to display messages from a certain level.

    Returns:
        (logging.Logger): An instance of the logging.Logger class.
    """
    channel_handler = logging.StreamHandler()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    if COLOR:
        cformat = "%(log_color)s" + log_format
        f = colorlog.ColoredFormatter(
            cformat,
            date_format,
            log_colors={
                "DEBUG": "bold_cyan",
                "INFO": "blue",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    else:
        f = logging.Formatter(log_format, date_format)
    channel_handler.setFormatter(f)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Only add Handler if not already present
    if not logger.handlers:
        logger.addHandler(channel_handler)

    return logger


def valid_url(url):
    """
    Verify and return the URL in a valid format.

    If the URL is missing the https prefix, the function will prepend the prefix
    after verifying that it's a valid base URL of an Central cluster.

    Args:
        url (str): Base URL for an HTTP request.

    Returns:
        (str): Valid base URL.

    Raises:
        ValueError: If the URL is invalid.
    """
    parsed_url = urlparse(url)
    if all([parsed_url.scheme, parsed_url.netloc]):
        return parsed_url.geturl()
    elif bool(parsed_url.scheme) is False and bool(parsed_url.path):
        parsed_url = parsed_url._replace(
            **{"scheme": "https", "netloc": parsed_url.path, "path": ""}
        )
        return parsed_url.geturl()
    else:
        raise ValueError(f"Invalid Base URL - {url}\n{URL_BASE_ERR_MESSAGE}")


def save_access_token(app_name, access_token, token_file_path, logger):
    """
    Update the access token for a specific application in the credentials file.

    Args:
        app_name (str): Name of the application to update (e.g., "new_central", "glp").
        access_token (str): The new access token value.
        token_file_path (str): Path to the credentials file.
        logger (logging.Logger): Logger instance to log messages.

    Raises:
        FileNotFoundError: If the credentials file doesn't exist.
        ValueError: If the app_name isn't found in the credentials file.
        IOError: If there is an error writing to the credentials file.
    """
    if not os.path.isfile(token_file_path):
        raise FileNotFoundError(f"Credentials file not found: {token_file_path}")

    # Load credentials file using existing helper function
    file_data = parse_input_file(token_file_path)
    _, ext = os.path.splitext(token_file_path)
    is_json = ext.lower() == ".json"

    # Update the access token for the specified app
    if app_name not in file_data:
        raise ValueError(f"App '{app_name}' not found in credentials file")

    file_data[app_name]["access_token"] = access_token

    # Write updated data back to file
    try:
        with open(token_file_path, "w") as f:
            if is_json:
                json.dump(file_data, f, indent=4, sort_keys=False)
            else:
                yaml.dump(file_data, f, sort_keys=False)
            logger.info(
                f"Successfully saved {app_name}'s access token in {token_file_path}"
            )
    except OSError as e:
        raise OSError(f"Failed to write updated credentials to file: {e}") from e
