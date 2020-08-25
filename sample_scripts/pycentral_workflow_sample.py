# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company

"""
Sample script shows making a REST API call to Aruba Central using 'pycentral.workflows'
and sub-module 'config_apsettings_from_csv.py'. In this sample script an API 
call is made to update AP settings such as AP hostname for multiple Access Points defined 
in the CSV file. 

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
    Filename in the following format. In this example, by providing only serial_number and name,
    an existing Access Point will be renamed. Other settings will remain as is.
    To not update a certain AP setting, leave it empty as shown below. 

    Sample CSV File
    ---------------
    serial_number,hostname,ip_address,zonename,achannel,atxpower,gchannel,gtxpower,dot11a_radio_disable,dot11g_radio_disable,usb_port_disable
    CNAAAA1234,AP1,0.0.0.0,,,,,,,,
    CNBBBB1234,AP2,0.0.0.0,,,,,,,,
"""

from pprint import pprint

# Create the following files by refering to the samples.
csv_filename = "csv_file.csv"
central_filename = "input_token_only.yaml"

# Get instance of ArubaCentralBase from the central_filename
from pycentral.workflows.workflows_utils import get_conn_from_file
central = get_conn_from_file(filename=central_filename)

# Rename AP using the workflow `workflows.config_apsettings_from_csv.py`
from pycentral.workflows.config_apsettings_from_csv import ApSettingsCsv
ApSettingsCsv(conn=central, csv_filename=csv_filename)
