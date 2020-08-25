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

"""This workflow updates the AP settings of existing APs and uses (2 * N) number of API calls. 
where 'N' is the number of APs in the provided CSV file.

1. Read the user provided ".csv" file with the following format.

    ------------------------------------------------------------
    serial_number,hostname,ip_address,zonename,achannel,atxpower,gchannel,gtxpower,dot11a_radio_disable,dot11g_radio_disable,usb_port_disable
    AAAAAAAAAA,AP1,0.0.0.0,,,,,,,,
    BBBBBBBBBB,AP2,0.0.0.0,,,,,,,,
    ------------------------------------------------------------

    * serial_number: Serial number of the AP for which the hostname will be modified
    * hostname: Set new name for the AP
    * ip_address: Should be 0.0.0.0 if AP obtains IP via DHCP. Set valid IP to change the IP of the AP
    * zonename: if provided, will be configured
    * achannel: if provided, will be configured
    * atxpower: if provided, will be configured
    * gchannel: if provided, will be configured
    * gtxpower: if provided, will be configured
    * dot11a_radio_disable: if provided, will be configured
    * dot11g_radio_disable: if provided, will be configured
    * usb_port_disable: if provided, will be configured

2. For every AP in the csv file, obtain existing settings of the AP and modify it based on csv file entries.

3. For every AP in the csv file, update AP settings via API call based on the data obtained from Step2. 

3. Display a list of failed APs at end of the script.
"""

import os, sys
import csv
from pprint import pprint

from pycentral.base import ArubaCentralBase
from pycentral.configuration import ApSettings
from pycentral.base_utils import console_logger
from pycentral.workflows.workflows_utils import get_conn_from_file, get_file_contents

LOGGER = console_logger("AP_SETTINGS_CSV")
ALL_FIELDS = ["serial_number", "hostname", "ip_address", "zonename", "achannel", 
              "atxpower", "gchannel", "gtxpower", "dot11a_radio_disable", 
              "dot11g_radio_disable", "usb_port_disable"]

def csv_file_dict(filename: str):
    """Read the APs from the provided csv file and check if all required fieldnames are present

    :param filename: Name of the csv file to read the AP settings data
    :type filename: str
    :raises UserWarning: Raises this exception when required column names are missing from csv file 
    :return: List of Python dict where each dict is representation of a row in csv file
    :rtype: list
    """
    try:
        ap_list = csv.DictReader(open(filename))
        csv_fields = ap_list.fieldnames
        if not set(ALL_FIELDS).issubset(csv_fields):
            set1 = set(ALL_FIELDS)
            set2 = set(csv_fields)
            missing = list(sorted(set1 - set2))
            raise UserWarning ("Missing fields in csv file %s" % str(missing))
        return ap_list
    except FileNotFoundError:
        LOGGER.error("File Not found.. "
                             "Provide absolute path for %s" % filename)
        LOGGER.error("Terminated module execution!")
    except Exception as err:
        LOGGER.error("Unable to process csv file: %s" % filename)
        LOGGER.error("Terminated module execution "
                             "with error: %s" % str(err))

def merge_apsettings_data(conn, ap_csv_data: dict):
    """Obtain existing AP settings via API call and modify the data based on the information 
    provided in the CSV file.

    :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
    :type conn: class:`pycentral.ArubaCentralBase` 
    :param ap_csv_data: One AP entry dict as read from a CSV file row
    :type ap_csv_data: dict
    :return: Merged data from existing AP settings and AP entry in the CSV file 
    :rtype: dict
    """
    aps = ApSettings()
    new_data = {}
    existing_data = {}
    get_resp = aps.get_ap_settings(conn, serial_number=ap_csv_data["serial_number"])
    if get_resp and get_resp["code"] == 200 and isinstance(get_resp["msg"], dict):
        existing_data = get_resp["msg"]
        for key in existing_data.keys():
            if key in ap_csv_data.keys() and ap_csv_data[key]:
                new_data[key] = ap_csv_data[key]
            else:
                new_data[key] = existing_data[key]
    else:
        conn.logger.error(get_resp)
    return new_data

def ApSettingsCsv(conn, csv_filename: str):
    """Function to modify existing AP's settings.

    :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
    :type conn: class:`pycentral.ArubaCentralBase` 
    :param csv_filename: Name of the CSV file in the format. To not modify some existing fields, leave it empty.
        serial_number,hostname,ip_address,zonename,achannel,atxpower,gchannel,gtxpower,dot11a_radio_disable,dot11g_radio_disable,usb_port_disable
        AAAAAAAAAA,AP1,0.0.0.0,,,,,,,,
        BBBBBBBBBB,AP2,0.0.0.0,,,,,,,,
    :type csv_filename: str
    """
    failed_aps = []
    success_aps = []
    all_aps = []
    aps = ApSettings()

    aps_data = csv_file_dict(filename=csv_filename)
    for ap_data in aps_data:
        all_aps.append(ap_data["serial_number"])
        merged_data = merge_apsettings_data(conn, ap_csv_data=ap_data)
        if not merged_data:
            failed_aps.append(ap_data["serial_number"])
            LOGGER.error("Failed to update ap settings for AP %s" % ap_data["serial_number"])
        else:
            resp = aps.update_ap_settings(conn, 
                                          serial_number=ap_data["serial_number"], 
                                          ap_settings_data=merged_data)
            if resp and resp["code"] == 200:
                success_aps.append(ap_data["serial_number"])
                LOGGER.info("API call successful to update settings for AP %s" % ap_data["serial_number"])
            else:
                failed_aps.append(ap_data["serial_number"])
                LOGGER.error("Failed to update ap settings for AP %s" % ap_data["serial_number"])

    unkown_aps = list(set(all_aps) - set(success_aps + failed_aps))
    failed_aps = failed_aps + unkown_aps
    print("")
    LOGGER.error("Failed to update ap settings for APs %s" % failed_aps)

