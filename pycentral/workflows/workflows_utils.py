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
import os
import json
import yaml
import csv

from pycentral.base import ArubaCentralBase


def get_file_contents(filename, logger=None):
    """Function to open a JSON/YAML/CSV file and return the contents of the\
        file in dict format. (A list of dict is returned for a CSV file.)

    :param filename: Name of an existing JSON/YAML/CSV file.
    :type filename: str
    :param logger: Provide an instance of class:`logging.logger`.
    :type logger: class:`logging.logger`, optional
    :raises UserWarning: Raises warning when supported filetypes are not\
        provided.
    :return: Data loaded from JSON/YAML/CSV file
    :rtype: dict (a list of dict for CSV)
    """
    read_data = {}
    try:
        with open(filename, "r") as fp:
            file_dummy, file_ext = os.path.splitext(filename)
            if ".json" in file_ext:
                read_data = json.loads(fp.read())
            elif file_ext in ['.yaml', '.yml']:
                read_data = yaml.safe_load(fp.read())
            elif ".csv" in file_ext:
                read_data = list(csv.DictReader(open(filename)))
            else:
                raise UserWarning("Provide valid file with"
                                  "format/extension [.json/.yaml/.yml/.csv]!")
        return read_data
    except FileNotFoundError:
        if logger:
            logger.error("File %s not found.." % filename)
        else:
            print("File %s Not Found!" % filename)
    except Exception as err:
        if logger:
            logger.error("Error reading file %s: %s" % (filename, str(err)))
        else:
            print(str(err))


def dict_list_to_csv(filename, csv_data_list, logger=None):
    """Write list of dictionaries into a CSV File via csv.DictWriter()

    :param filename: Name of the file to be created or overwritten
    :type filename: str
    :param csv_data_list: A list of dictionaries, where each dict is a row in\
        CSV file
    :type csv_data_list: list
    :param logger: Provide an instance of class:`logging.logger`.
    :type logger: class:`logging.logger`, optional
    """
    csv_columns = []
    if csv_data_list and csv_data_list[0]:
        csv_columns = list(csv_data_list[0].keys())
    else:
        if logger:
            logger.warning("No data to write to a CSV file...")
        return
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in csv_data_list:
                writer.writerow(data)
        if logger:
            logger.info(
                "Creating a new csv file '%s' with failed APs..." %
                filename)
    except IOError:
        print("I/O error")
    except Exception as err:
        if logger:
            logger.error("Error writing to file %s: %s" % (filename, str(err)))
        else:
            print(str(err))


def get_conn_from_file(filename, account=None, logger=None):
    """Creates an instance of class`pycentral.ArubaCentralBase` based on the\
        information
    provided in the YAML/JSON file. \n
        * keyword central_info: A dict containing arguments as accepted by\
            class`pycentral.ArubaCentralBase` \n
        * keyword ssl_verify: A boolean when set to True, the python client\
            validates Aruba Central's SSL certs. \n
        * keyword token_store: Optional. Defaults to None. \n

    :param filename: Name of a JSON/YAML file containing the keywords required\
        for class:`pycentral.ArubaCentralBase`
    :type filename: str
    :param logger: Provide an instance of class:`logging.logger`, defaults to\
        logger class with name "ARUBA_BASE".
    :type logger: class:`logging.logger`, optional
    :return: An instance of class:`pycentral.ArubaCentralBase` to make API\
        calls and manage access tokens.
    :rtype: class:`pycentral.ArubaCentralBase`
    """
    conn = None
    token_store = None
    ssl_verify = True

    input_args = get_file_contents(filename=filename, logger=logger)
    if not input_args:
        sys.exit("Unable to get the file content... exiting!")
    # if "central_info" not in input_args:
    #     sys.exit("exiting... Provide central_info in the file %s" % filename)
    # central_info = input_args["central_info"]

    if account is None:
        account = "central_info"
    if account not in input_args:
        sys.exit("exiting... Provide %s in the file %s" % (account, filename))
    central_info = input_args[account]

    if "token_store" in input_args:
        token_store = input_args["token_store"]
    if "ssl_verify" in input_args:
        ssl_verify = input_args["ssl_verify"]

    conn = ArubaCentralBase(central_info=central_info,
                            token_store=token_store,
                            ssl_verify=ssl_verify,
                            logger=logger)
    return conn
