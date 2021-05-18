# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company

"""
Sample script shows making how to use existing automation workflows 'pycentral.workflows'.
In this sample, AP renaming workflow for APs in the UI group is shown. The CSV file can be downloaded
from the Central UI. Using the CSV file, update the AP names. 'config_apsettings_from_csv.py'.ß

1. central_filename:
    The format for input file is provided in the files 'input_credentials' and 'input_token_only'.
    Files in JSON and YAML formats are supported. Use either credentials based file or token based file.

    * Credentials based file will generate new access token using OAUTH API and cache the token locally.
        Sample file in YAML format
        --------------------------
            central_info:
                username: "<aruba-central-account-username>"
                password: "<aruba-central-account-password>"
                client_id: "<api-gateway-client-id>"
                client_secret: "<api-gateway-client-secret>"
                customer_id: "<aruba-central-customer-id>"
                base_url: "<api-gateway-domain-url>"
            token_store:
                type: "local"
                path: "temp"
            ssl_verify: true

    * Token based file will directly use the API access token and will not cache the token locally.
        Sample file in YAML format
        --------------------------
            central_info:
                base_url: "<api-gateway-domain-url>"
                token:
                    access_token: "<api-gateway-access-token>"
            ssl_verify: true

2. csv_filename:
    A CSV file as downloaded from the Aruba Central UI,
        * "Account Home -> Network Operations -> Pick a group from Global drop-down -> Devices -> Access Points"
        * Click on the "Download CSV" icon/button to download the CSV file.

    The following fields can also be added to the CSV file manually. Complete list of the fields are shown below.
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
    Only these fields in the CSV file will be updated.
"""

# Create the following files by refering to the samples/documentation.
csv_filename = "csv_file.csv"
central_filename = "input_token_only.yaml"

# Get instance of ArubaCentralBase from the central_filename
from pycentral.workflows.workflows_utils import get_conn_from_file
central = get_conn_from_file(filename=central_filename)

# Rename AP using the workflow `workflows.config_apsettings_from_csv.py`
from pycentral.workflows.config_apsettings_from_csv import ApSettingsCsv
ap_workflow = ApSettingsCsv(is_dhcp_ip=True)
ap_workflow.ap_settings_csv(conn=central, csv_filename=csv_filename)