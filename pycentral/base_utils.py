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

import logging
import os
from urllib.parse import urlencode, urlparse, urlunparse
try:
    import colorlog  # type: ignore
    COLOR = True
except (ImportError, ModuleNotFoundError):
    COLOR = False

C_LOG_LEVEL = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0
}

C_DEFAULT_ARGS = {
    "base_url": None,
    "client_id": None,
    "client_secret": None,
    "customer_id": None,
    "username": None,
    "password": None,
    "token": None
}


def parseInputArgs(central_info):
    """This method parses user input, checks for the availability of mandatory\
        arguments. Optional missing parameters in central_info variable is\
        initialized as defined in C_DEFAULT_ARGS.

    :param central_info: central_info dictionary as read from user's input\
        file.
    :type central_info: dict
    :return: parsed central_info dict with missing optional params set to\
        default values.
    :rtype: dict
    """
    if not central_info:
        exit("Error: Invalid Input!")

    # Mandatory input arg
    if "base_url" not in central_info:
        exit("Error: Provide base_url for API Gateway!")

    default_dict = dict(C_DEFAULT_ARGS)
    for key in default_dict.keys():
        if key in central_info:
            default_dict[key] = central_info[key]

    return default_dict


def tokenLocalStoreUtil(token_store, customer_id="customer",
                        client_id="client"):
    """Utility function for storeToken and loadToken default access token\
        storage/cache method. This function generates unique file name for a\
        customer and API gateway client to store and load access token in the\
        local machine for reuse. The format of the file name is\
        tok_<customer_id>_<client_id>.json. If customer_id or client_id is not\
        provided, default values mentioned in args will be used.

    :param token_store: Placeholder to support different token storage\
        mechanism. \n
        * keyword type: Place holder for different token storage mechanism.\
            Defaults to local storage. \n
        * keyword path: path where temp folder is created to store token JSON\
            file. \n
    :type token_store: dict
    :param customer_id: Aruba Central customer id, defaults to "customer"
    :type customer_id: str, optional
    :param client_id: API Gateway client id, defaults to "client"
    :type client_id: str, optional
    :return: Filename for access token storage.
    :rtype: str
    """
    fileName = "tok_" + str(customer_id)
    fileName = fileName + "_" + str(client_id) + ".json"
    filePath = os.path.join(os.getcwd(), "temp")
    if token_store and "path" in token_store:
        filePath = os.path.join(token_store["path"])
    fullName = os.path.join(filePath, fileName)
    return fullName


def get_url(base_url, path='', params='', query={}, fragment=''):
    """This method constructs complete URL based on multiple parts of URL.

    :param base_url: base url for a HTTP request
    :type base_url: str
    :param path: API endpoint path, defaults to ''
    :type path: str, optional
    :param params: API endpoint path parameters, defaults to ''
    :type params: str, optional
    :param query: HTTP request url query parameters, defaults to {}
    :type query: dict, optional
    :param fragment: URL fragment identifier, defaults to ''
    :type fragment: str, optional
    :return: Parsed URL
    :rtype: class:`urllib.parse.ParseResult`
    """
    parsed_baseurl = urlparse(base_url)
    scheme = parsed_baseurl.scheme
    netloc = parsed_baseurl.netloc
    query = urlencode(query)
    url = urlunparse((scheme, netloc, path, params, query, fragment))
    return url


def console_logger(name, level="DEBUG"):
    """This method create an instance of python logging and sets the following\
        format for log messages.\n<date> <time> - <name> - <level> - <message>

    :param name: String displayed after data and time. Define it to identify\
        from which part of the code, log message is generated.
    :type name: str
    :param level: Loggin level set to display messages from a certain logging\
        level. Refer Python logging library man page, defaults to "DEBUG"
    :type level: str, optional
    :return: An instance of class logging
    :rtype: class:`logging.Logger`
    """
    channel_handler = logging.StreamHandler()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = '%Y-%m-%d %H:%M:%S'
    f = format
    if COLOR:
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(
            cformat,
            date_format,
            log_colors={
                'DEBUG': 'bold_cyan',
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red'})
    else:
        f = logging.Formatter(format, date_format)
    channel_handler.setFormatter(f)

    logger = logging.getLogger(name)
    logger.setLevel(C_LOG_LEVEL[level])
    logger.addHandler(channel_handler)

    return logger
