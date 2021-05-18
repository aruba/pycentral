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

"""This workflow updates the AP settings of existing APs in the UI group and uses (2 * N) number of API calls.
where 'N' is the number of APs in the provided CSV file.

1. Read the user provided ".csv" file containing the following fields. CSV file can be downloaded from the
    central UI contains. It downloaded CSV file contains "SERIAL,DEVICE NAME,IP ADDRESS,ZONE" fields. Complete list of
    fields accepted by the 'AP Settings' API endpoint are shown below.

    * SERIAL: Serial number of the AP for which the hostname will be modified
    * DEVICE NAME: Set new name for the AP
    * IP ADDRESS: Set valid IP to change the IP of the AP. If the AP has DHCP based IP, set "is_dhcp_ip" flag to true.
    * ZONE: if provided, will be configured
    * A CHANNEL: if provided, will be configured
    * A TX POWER: if provided, will be configured
    * G CHANNEL: if provided, will be configured
    * G TX POWER: if provided, will be configured
    * DOT11A RADIO DISABLE: if provided, will be configured
    * DOT11G RADIO DISABLE: if provided, will be configured
    * USB PORT DISABLE: if provided, will be configured

2. For every AP in the csv file, obtain existing settings of the AP and modify it based on csv file entries.

3. For every AP in the csv file, update AP settings via API call based on the data obtained from Step2.

3. Display a list of failed APs at end of the script. Additionally generate a CSV file with the failed APs.
"""

import os, sys
from pycentral.configuration import ApSettings
from pycentral.base_utils import console_logger
from pycentral.workflows.workflows_utils import dict_list_to_csv, get_file_contents

class CsvField():
    """Internal helper class to map csv fields to API endpoint payload fields
    """
    def __init__(self, name, default=None):
        self.name = name
        self.default = default

LOGGER = console_logger("AP_SETTINGS_CSV")
ALL_FIELDS = ["SERIAL", "DEVICE NAME", "IP ADDRESS", "ZONE", "A CHANNEL",
              "A TX POWER", "G CHANNEL", "G TX POWER", "DOT11A RADIO DISABLE",
              "DOT11G RADIO DISABLE", "USB PORT DISABLE"]
CSV_MAPPING = {
    "hostname": CsvField("DEVICE NAME"),
    "serial_number": CsvField("SERIAL"),
    "ip_address": CsvField("IP ADDRESS", default="0.0.0.0"),
    "zonename": CsvField("ZONE"),
    "achannel": CsvField("A CHANNEL"),
    "gchannel": CsvField("G CHANNEL"),
    "atxpower": CsvField("A TX POWER"),
    "gtxpower": CsvField("G TX POWER"),
    "dot11a_radio_disable": CsvField("DOT11A RADIO DISABLE"),
    "dot11g_radio_disable": CsvField("DOT11G RADIO DISABLE"),
    "usb_port_disable": CsvField("USB PORT DISABLE")
}

class ApSettingsCsv():
    """Bulk configure APs in the Central UI group via 'AP Settings' API. The CSV file can be downloaded from the
    Central UI and more fields can be added to it. However, the functionality is limited as supported by the
    "AP Settings" API endpoint.
    """
    def __init__(self, is_dhcp_ip: bool = False):
        """Constructor for the class

        :param is_dhcp_ip: True if IAP has DHCP based IP. When True, the IP address defined in the CSV file
            will be ignore and "0.0.0.0" value will be used as recommended, defaults to False
        :type is_dhcp_ip: bool, optional
        """
        self.is_dhcp_ip = is_dhcp_ip

    def merge_apsettings_data(self, conn, ap_csv_data: dict):
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
        get_resp = aps.get_ap_settings(conn, serial_number=ap_csv_data["SERIAL"])
        if get_resp and get_resp["code"] == 200 and isinstance(get_resp["msg"], dict):
            existing_data = get_resp["msg"]
            for key in existing_data.keys():
                if key == "ip_address" and self.is_dhcp_ip:
                    new_data[key] = CSV_MAPPING[key].default
                    continue
                csv_key = CSV_MAPPING[key].name
                if csv_key in ap_csv_data.keys() and ap_csv_data[csv_key]:
                    new_data[key] = ap_csv_data[csv_key]
                else:
                    new_data[key] = existing_data[key]
        else:
            conn.logger.error(get_resp)
        return new_data

    def csv_data_formatter(self, failed_aps, existing_csv_data):
        failed_ap_list = []
        for ap_serial in failed_aps:
            for ap in existing_csv_data:
                if ap["SERIAL"] == ap_serial:
                    failed_ap_list.append(ap)
        return failed_ap_list

    def ap_settings_csv(self, conn, csv_filename: str):
        """Function to modify existing AP's settings.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param csv_filename: Name of the CSV file downloaded from Central UI. These fields
            from the CSV file are used "SERIAL,DEVICE NAME,IP ADDRESS,ZONE". The additional fields
            that can defined are as follows "A CHANNEL,A TX POWER,G CHANNEL,G TX POWER,
            DOT11A RADIO DISABLE,DOT11G RADIO DISABLE,USB PORT DISABLE".
        :type csv_filename: str
        """
        failed_aps = []
        success_aps = []
        all_aps = []
        aps = ApSettings()
        failed_ap_list = []

        aps_data = get_file_contents(filename=csv_filename, logger=LOGGER)
        if not aps_data:
            sys.exit("Unable to read from file %s... exiting!" % csv_filename)

        for ap_data in aps_data:
            if "SERIAL" in ap_data:
                ap_serial = ap_data["SERIAL"]
            else:
                LOGGER.error("Field name 'SERIAL' not found in the csv file %s" % csv_filename)
                sys.exit("exiting...")
            all_aps.append(ap_serial)
            merged_data = self.merge_apsettings_data(conn, ap_csv_data=ap_data)
            if not merged_data:
                failed_aps.append(ap_serial)
                LOGGER.error("Failed to update ap settings for AP %s" % ap_serial)
            else:
                resp = aps.update_ap_settings(conn,
                                            serial_number=ap_serial,
                                            ap_settings_data=merged_data)
                if resp and resp["code"] == 200:
                    success_aps.append(ap_serial)
                    LOGGER.info("API call successful to update settings for AP %s" % ap_serial)
                else:
                    failed_aps.append(ap_serial)
                    LOGGER.error("Failed to update ap settings for AP %s" % ap_serial)

        unkown_aps = list(set(all_aps) - set(success_aps + failed_aps))
        failed_aps = failed_aps + unkown_aps
        if failed_aps:
            failed_ap_list = self.csv_data_formatter(failed_aps, aps_data)

            file_dummy, file_ext = os.path.splitext(csv_filename)
            failed_filename =  file_dummy + "_failed" + file_ext
            dict_list_to_csv(filename=failed_filename, csv_data_list=failed_ap_list ,logger=LOGGER)

            LOGGER.error("\nFailed to update ap settings for APs %s" % failed_aps)