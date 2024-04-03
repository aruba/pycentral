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

DEVICE_TYPES = ["IAP", "ArubaSwitch", "CX", "MobilityController"]

# Dictionary of Public Aruba Cluster Names with their corresponding API Base
# URLs. You can update this dictionary, if you want to add your own private
# Aruba cluster details
CLUSTER_API_BASE_URL_LIST = {
    "US-1": "app1-apigw.central.arubanetworks.com",
    "US-2": "apigw-prod2.central.arubanetworks.com",
    "US-East1": "apigw-us-east-1.central.arubanetworks.com",
    "US-West4": "apigw-uswest4.central.arubanetworks.com",
    "EU-1": "eu-apigw.central.arubanetworks.com",
    "EU-Central2": "apigw-eucentral2.central.arubanetworks.com",
    "EU-Central3": "apigw-eucentral3.central.arubanetworks.com",
    "Canada-1": "apigw-ca.central.arubanetworks.com",
    "China-1": "apigw.central.arubanetworks.com.cn",
    "APAC-1": "api-ap.central.arubanetworks.com",
    "APAC-EAST1": "apigw-apaceast.central.arubanetworks.com",
    "APAC-SOUTH1": "apigw-apacsouth.central.arubanetworks.com",
    "UAE-NORTH1": "apigw-uaenorth1.central.arubanetworks.com"
}
