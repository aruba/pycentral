# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company

"""
Sample script shows making a REST API call to Aruba Central using base module
`pycentral.pycentral.base` and function `command()`. In this sample script an 
API call is made to obtain list of existing groups. 

1. central_info:
        Either provide the following Aruba Central credentials [or] 
        use API Gateway Access Token

        central_info = {
            "username": "<aruba-central-account-username>",
            "password": "<aruba-central-account-password>",
            "client_id": "<api-gateway-client-id>",
            "client_secret": "<api-gateway-client-secret>",
            "customer_id": "<aruba-central-customer-id>",
            "base_url": "<api-gateway-domain-url>"
        }

        [OR]

        central_info = {
            "base_url": "<api-gateway-domain-url>",
            "token": {
                "access_token": "<api-gateway-access-token>"
            }
        }

2. token_store:
        When (username, password, client_id, client_secret and customer_id) are provided in central_info,
        a new access token will be generated and by default cached locally under `temp` dir. To prevent 
        caching directly provide `token` in `central_info` (instead of username, password, client_id, 
        client_secret and customer_id).

        To modify where the token is stored, use the following variable.

        token_store = {
            "type": "local",
            "path": "temp"
        }

3. ssl_verify:
        To disable Python Client to validate SSL certs, set ssl_verify to False. By default, set to True.

        ssl_verify = True
"""

# Import Aruba Central Base
from pycentral.base import ArubaCentralBase
from pprint import pprint

# Create an instance of ArubaCentralBase using API access token 
# or API Gateway credentials.
central_info = {
    "base_url": "<api-gateway-domain-url>",
    "token": {
        "access_token": "<api-gateway-access-token>"
    }
}
ssl_verify = True
central = ArubaCentralBase(central_info=central_info,
                           ssl_verify=ssl_verify)

# Sample API call using 'ArubaCentralBase.command()'
# GET groups from Aruba Central
apiPath = "/configuration/v2/groups"
apiMethod = "GET"
apiParams = {
    "limit": 20,
    "offset": 0
}
base_resp = central.command(apiMethod=apiMethod, 
                            apiPath=apiPath,
                            apiParams=apiParams)
pprint(base_resp)
