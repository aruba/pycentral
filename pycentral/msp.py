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

from pycentral.base_utils import console_logger
from pycentral.url_utils import urlJoin, MspURL

urls = MspURL()
logger = console_logger("MSP")


class MSP(object):
    """A python class consisting of functions to manage Aruba Central's MSP \
        mode via REST API
    """

    def get_customers(self, conn, offset=0, limit=100, customer_name=None):
        """This function returns the list of customers based on the provided \
            parameters

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param offset: Pagination start index, defaults to 0
        :type offset: int, optional
        :param limit: Pagination end index, defaults to 100
        :type limit: int, optional
        :param customer_name: Filter on customer name, defaults to None.
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        apiPath = urls.MSP["V1_CUSTOMER"]
        apiParams = {
            "offset": offset,
            "limit": limit
        }
        if customer_name is not None:
            apiParams['customer_name'] = customer_name
        resp = conn.command(apiMethod="GET",
                            apiPath=apiPath,
                            apiParams=apiParams)
        if resp['code'] == 200:
            log_message = 'Successfully fetched list of customers based on' \
                ' the provided API parameters'
            logger.info(log_message)
        return resp

    def get_all_customers(self, conn):
        """This function returns a list of all the customers in the MSP \
            account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :return: Returns list of dictionaries. Each dictionary has the\
            following keys associated with a customer - account_status,\
            account_type, ap_config_diff, application_id,\
            application_instance_id, created_at, customer_id, customer_name,\
            description, device_quota, hppc_config_diff, lock_msp_ssids,\
            msp_conversion_status, msp_id, platform_customer_details,\
            platform_customer_id, provision_status, region, switch_config_diff,\
            updated_at, username
        :rtype: list
        """
        offset = 0
        limit = 100
        customer_list = []
        while True:
            resp = self.get_customers(conn, offset=offset, limit=limit)
            if resp['code'] == 200:
                resp_message = resp['msg']
                resp_customers = resp_message['customers']
                if (len(resp_customers) > 0):
                    customer_list.extend(resp_customers)
                if resp_message['total'] == len(customer_list):
                    break
            else:
                log_message = f'Response code {resp["code"]}. ' \
                    'Error in fetching list of customers.'
                logger.error(log_message)
                return
            offset += limit
        return customer_list

    def create_customer(self, conn, customer_details):
        """This function creates a customer in the MSP account based on the \
            provided customer details

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_details: Details of customer that has to be created. \
            The customer details should have the following the keys -\
            customer_name, country_name, street_address, city, state,\
            country_name, zip_postal_code. These keys are optional - \
            lock_msp_ssids, description, group_name
        :type customer_details: dict
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        apiPath = urls.MSP["V2_CUSTOMER"]
        if self.__validate_customer_attributes__(customer_details):
            customer_apiData = self.__create_customer_body__(conn, customer_details)
            resp = conn.command(apiMethod="POST",
                                apiPath=apiPath,
                                apiData=customer_apiData)
            if resp['code'] == 201:
                logger.info(
                    f'Successfully created customer {customer_details["name"]}')
            return resp

    def __validate_customer_attributes__(self, customer_details):
        """This function verifies the customer details to ensure that the\
            necessary parameters for the "create customer" API are present in\
            the customer details body.
        :param customer_details: Details of customer that has to be created. \
            The customer details should have the following the keys -\
            customer_name, country_name, street_address, city, state,\
            country_name, zip_postal_code. These keys are optional - \
            lock_msp_ssids, description, group_name
        :type customer_details: dict
        :return: True when the necessary parameters are available in the\
            customer details.
        :rtype: bool
        """
        required_keys = ["customer_name", "country_name", "street_address",
                         "city", "state", "country_name", "zip_postal_code"]
        missingKey = True
        for key in required_keys:
            if key not in customer_details:
                log_message = f'Missing required key {key} & value in customer'\
                    'details. Please add the missing key before calling the function.'
                logger.error(log_message)
                missingKey = False
        return missingKey

    def __create_customer_body__(self, conn, customer_details):
        """This function creates the create customer API's body\

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_details: Details of customer that has to be created. \
            The customer details should have the following the keys -\
            customer_name, country_name, street_address, city, state,\
            country_name, zip_postal_code. These keys are optional - \
            lock_msp_ssids, description, group_name
        :type customer_details: dict
        :return: Dictionary that has the customer details structured for the\
            customer API body
        :rtype: dict
        """
        if (len(customer_details["country_name"]) > 2):
            country_code = self.get_country_code(
                conn, customer_details["country_name"])
            if country_code is not None:
                customer_details["country_name"] = self.get_country_code(
                    conn, customer_details["country_name"])
            else:
                log_message = f'Unable to find {customer_details["country_name"]}.'\
                    "Please provide a valid country name. Please check out " \
                    "get_country_codes_list function to get list of valid " \
                    "countries/country codes"
                logger.error(log_message)
                return

        customer_JSON = {
            "customer_name": customer_details['customer_name'],
            "description": "",
            "lock_msp_ssids": False,
            "address": {
                "street_address": customer_details['street_address'],
                "city": customer_details['city'],
                "state": customer_details['state']
            },
            "country_name": customer_details['country_name'],
            "zip_postal_code": customer_details['zip_postal_code']
        }
        optional_keys = ["lock_msp_ssids", "description"]
        for key in optional_keys:
            if key in customer_details:
                customer_JSON[key] = customer_details[key]

        if 'group_name' in customer_details and len(
                customer_details['group_name']) > 0:
            customer_JSON['group'] = {
                "name": customer_details['group_name'],
            }
        return customer_JSON

    def update_customer(
            self,
            conn,
            customer_details,
            customer_id=None,
            customer_name=None):
        """This function updates the details of an existing customer in the \
            MSP account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_details: Details of customer that has to be updated. \
            The customer details should have the following the keys -\
            customer_name, country_name, street_address, city, state,\
            country_name, zip_postal_code. These keys are optional - \
            lock_msp_ssids, description, group_name
        :type customer_details: dict
        :param customer_id: Customer ID of the customer, defaults to None.
        :type customer_id: str, optional        
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if customer_details is None:
            logger.error("Attribute Error. Please pass in customer details")
            return

        if customer_id is None and customer_name is None:
            logger.error(
                "Attribute Error. Pass either customer_id or customer_name")
            return

        elif customer_id is None and customer_name:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                log_message = 'Unable to get customer_id. Please provide a ' \
                    'valid customer name'
                logger.error(log_message)
                return

        if self.__validate_customer_attributes__(customer_details):
            customer_apiData = self.__create_customer_body__(conn, customer_details)
            apiPath = f'{urls.MSP["V2_CUSTOMER"]}/{customer_id}'
            resp = conn.command(
                apiMethod="PUT",
                apiPath=apiPath,
                apiData=customer_apiData)
            if resp['code'] == 200:
                logger.info(
                    f'Successfully updated customer {customer_details["customer_name"]}')
            return resp

    def delete_customer(self, conn, customer_id=None, customer_name=None):
        """This function deletes the customer in the MSP account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_id: Customer ID of the customer, defaults to None.
        :type customer_id: str, optional        
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if customer_id is None and customer_name is None:
            logger.error(
                "Attribute Error. Pass either customer_id or customer_name")
            return
        elif customer_id is None and customer_name:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                logger.error(
                    'Unable to get customer_id. Please provide a valid customer name')
                return

        apiPath = f'{urls.MSP["V1_CUSTOMER"]}/{customer_id}'
        resp = conn.command(apiMethod="DELETE", apiPath=apiPath)
        if resp['code'] == 200:
            logger.info(
                f'Successfully deleted customer with customer-id - {customer_id}')
        return resp

    def get_customer_details(self, conn, customer_id=None, customer_name=None):
        """This function fetches the details of the customer in the MSP account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_id: Customer ID of the customer, defaults to None.
        :type customer_id: str, optional        
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if customer_id is None and customer_name is None:
            logger.error(
                "Attribute Error. Pass either customer_id or customer_name")
            return None

        elif customer_id is None and customer_name:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                logger.error(
                    'Unable to get customer_id. Please provide a valid customer name')
                return

        apiPath = f'{urls.MSP["V1_CUSTOMER"]}/{customer_id}'
        resp = conn.command(apiMethod="GET", apiPath=apiPath)
        if (resp["code"] == 200):
            log_message = "Successfully fetched details of customer with " \
                f"customer-id - {customer_id}"
            logger.info(log_message)
        return resp

    def get_customer_id(self, conn, customer_name=None):
        """This function fetches the customer id of the customer based on the\
            customer name.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`      
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: Customer ID of the customer. It will return None if no\
            customer is found
        :rtype: string
        """
        if not customer_name:
            log_message = 'Unable to find customer ID when no customer name is '\
                'passed. Please provide a valid customer name'
            logger.error(log_message)
            return None

        apiPath = urls.MSP["V1_CUSTOMER"]
        apiParams = {
            "customer_name": customer_name
        }
        resp = conn.command(
            apiMethod="GET",
            apiPath=apiPath,
            apiParams=apiParams)
        if (resp["code"] == 200 and len(resp['msg']['customers']) > 0):
            for customer in resp['msg']['customers']:
                if customer['customer_name'] == customer_name:
                    return resp['msg']['customers'][0]['customer_id']
        logger.error(f'Unable to find customer_id of {customer_name}.')
        return None

    def get_msp_id(self, conn):
        """This function fetches the MSP ID of the MSP.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`      
        :return: MSP ID of the MSP account. It will return None if no\
            ID is found
        :rtype: string
        """
        customer_response = self.get_customers(conn, offset=0, limit=100)
        customer_list = customer_response['msg']['customers']
        for customer in customer_list:
            if 'msp_id' in customer:
                return customer['msp_id']
        return None

    def get_country_code(self, conn, country_name):
        """This function fetches the country code of a country. This country\
            code is needed for the Create Customer API

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`      
        :param country_name: Name of country
        :type country_name: str
        :return: Country Code of country. It will return None if no\
            country is found
        :rtype: string
        """
        country_list = self.get_country_codes_list(conn)['msg']
        if country_name in country_list:
            return country_list[country_name]
        return None

    def get_country_codes_list(self, conn):
        """This function fetches the dictionary of the country codes of countries. \
            The keys of the dictionary are the country names and the values\
            are the country codes

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`  
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        apiPath = urls.MSP["COUNTRY_CODE"]
        resp = conn.command(apiMethod="GET", apiPath=apiPath)
        if resp['code'] == 200:
            logger.info('Successfully fetched country code list')
        return resp

    def get_msp_users(self, conn, offset=0, limit=10):
        """This function returns the list of users under the MSP account\
            based on the provided parameters

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param offset: Pagination start index, defaults to 0
        :type offset: int, optional
        :param limit: Pagination end index, defaults to 10
        :type limit: int, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        apiPath = urls.MSP["USERS"]
        apiParams = {
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET",
                            apiPath=apiPath, apiParams=apiParams)
        if (resp['code'] == 200 and resp['msg']['status'] == "success"):
            logger.info('Successfully fetched users in the MSP account')
        return resp

    def get_customer_users(
            self,
            conn,
            offset=0,
            limit=10,
            customer_id=None,
            customer_name=None):
        """This function returns the list of users under a customer in the \
            MSP account based on the provided parameters

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param offset: Pagination start index, defaults to 0
        :type offset: int, optional
        :param limit: Pagination end index, defaults to 10
        :type limit: int, optional
        :param customer_id: Customer ID of the customer, defaults to None.
        :type customer_id: str, optional        
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if customer_id is None and customer_name is None:
            logger.error(
                "Attribute Error. Provide either customer_id or customer_name")
            return
        elif customer_id is None and customer_name:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                log_message = f'Unable to get customer_id of {customer_name}.' \
                    'Please provide a valid customer name'
                logger.error(log_message)
                return

        apiPath = urls.MSP["USERS"].split('/')
        apiPath.insert(-1, customer_id)
        apiPath = '/'.join(apiPath)

        apiParams = {
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET",
                            apiPath=apiPath, apiParams=apiParams)
        if (resp['code'] == 200):
            logger.info('Successfully fetched users in the customer account')
        return resp

    def get_msp_resources(self, conn):
        """This function returns the branding resources under an MSP account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        apiPath = urls.MSP["RESOURCES"]
        resp = conn.command(apiMethod="GET",
                            apiPath=apiPath)
        if (resp['code'] == 200):
            logger.info('Successfully fetched resources under the MSP')
        return resp

    def edit_msp_resources(self, conn, resources_dict):
        """This function edits the branding resources under an MSP account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param resources_dict: Details of new branding resources of the MSP.\
            This parameter's structure should match the structure of the\
            sample API body in the Swagger.
        :type resources_dict: dict
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        apiPath = urls.MSP["RESOURCES"]
        apiData = resources_dict
        resp = conn.command(apiMethod="PUT",
                            apiPath=apiPath,
                            apiData=apiData)
        if (resp['code'] == 200):
            return resp['msg']
        return resp

    def get_customer_devices_and_subscriptions(
            self,
            conn,
            customer_id=None,
            customer_name=None,
            offset=0,
            limit=10,
            device_type=None):
        """This function gets the devices & subscriptions under the customer\
            account based on the provided parameters

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_id: Customer ID of the customer, defaults to None.
        :type customer_id: str, optional        
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :param offset: Pagination start index, defaults to 0
        :type offset: int, optional
        :param limit: Pagination end index, defaults to 10
        :type limit: int, optional
        :param device_type: Filter on device_type. Accepted values - iap,\
            switch, all_controller. Defaults to None. 
        :type device_type: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if customer_id is None and customer_name is None:
            logger.error(
                "Attribute Error. Provide either customer_id or customer_name")
            return

        elif customer_id is None and customer_name:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                logger.error(
                    'Unable to get customer_id. Please provide a valid customer name')
                return

        apiPath = f'{urls.MSP["V1_CUSTOMER"]}/{customer_id}/devices'
        apiParams = {
            "offset": offset,
            "limit": limit
        }
        if device_type is not None:
            apiParams['device_type'] = device_type
        resp = conn.command(apiMethod="GET",
                            apiPath=apiPath,
                            apiParams=apiParams)
        if (resp['code'] == 200 and 'status' in resp['msg']
                and resp['msg']['status'] == 'success'):
            log_message = 'Successfully fetched devices & subscriptions in the' \
                ' customer account'
            logger.info(log_message)
        return resp

    def assign_devices_to_customers(
            self,
            conn,
            devices,
            group_name=None,
            customer_id=None,
            customer_name=None):
        """This function assign devices to customer

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param devices: List of dictionaries of devices that will be assigned\
            to the customer account. Each dictionary corresponds to a device &\
            will have the following keys - serial, mac
        :type devices: list
        :param group_name: Name of the group to which the devices will be\
            moved to within the customer.
        :type group_name: str, optional
        :param customer_id: Customer ID of the customer, defaults to None.
        :type customer_id: str, optional       
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if devices is None:
            log_message = 'Attribute Error. Please provide list of devices that'\
                'should be moved to the customer'
            logger.error(log_message)
            return

        if customer_id is None and customer_name is None:
            logger.error(
                "Attribute Error. Provide either customer_id or customer_name")
            return

        elif customer_id is None and customer_name:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                log_message = 'Unable to get customer_id. Please provide a'\
                    'valid customer name'
                logger.error(log_message)
                return

        apiPath = f'{urls.MSP["V1_CUSTOMER"]}/{customer_id}/devices'
        apiData = {
            "devices": devices
        }
        if group_name is not None:
            apiData['group'] = group_name

        resp = conn.command(apiMethod="PUT",
                            apiPath=apiPath,
                            apiData=apiData)
        if (resp['code'] == 200 and 'status_code' in resp['msg']
                and resp['msg']['status_code'] == 200):
            device_serials = ", ".join(device["serial"] for device in devices)
            log_message = f"Successfully moved devices {device_serials} " \
                "to customer\'s Central Instance"
            logger.info(log_message)
        return resp

    def unassign_devices_from_customers(self, conn, devices, msp_id=None):
        """This function unassign devices from the customer to the MSP's \
            device inventory

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param devices: List of dictionaries of devices that will be assigned\
            to the customer account. Each dictionary corresponds to a device &\
            will have the following keys - serial, mac
        :type devices: list
        :param msp_id: ID of the MSP account. If no ID is provided, then the\
            the msp_id will be fetched with the get_msp_id function
        :type msp_id: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if devices is None:
            log_message = 'Attribute Error. Please provide list of devices that' \
                ' should be moved from the customer to the MSP device inventory.'
            logger.error(log_message)
            return

        if msp_id is None:
            msp_id = self.get_msp_id(conn)
            if msp_id is None:
                logger.error("Attribute Error. Unable to find MSP ID")
            return

        apiPath = f'{urls.MSP["V1_CUSTOMER"]}/{msp_id}/devices'
        apiData = {
            "devices": devices
        }

        resp = conn.command(apiMethod="PUT",
                            apiPath=apiPath,
                            apiData=apiData)
        if (resp['code'] == 200 and 'status_code' in resp['msg']
                and resp['msg']['status_code'] == 200):
            log_message = "Successfully moved devices" + \
                {", ".join(device["serial"] for device in devices)} + \
                "from customer\'s Central Instance to MSP's device inventory."
            logger.info(log_message)
        return resp

    def unassign_all_customer_device(
            self,
            conn,
            customer_id=None,
            customer_name=None):
        """This function unassigns all devices & subscriptions from a\
            customer's Central Instance. It will move these devices &\
            subsciptions to the MSP's device & subscription inventory.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_id: Customer ID of the customer, defaults to None.
        :type customer_id: str, optional            
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        if customer_id is None and customer_name is None:
            logger.error(
                "Attribute Error. Provide either customer_id or customer_name")
            return

        elif customer_id is None and customer_name:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                log_message = 'Unable to get customer_id. Please provide a ' \
                    'valid customer name'
                logger.error(log_message)
                return

        apiSubPath = "/".join(urls.MSP["V2_CUSTOMER"].split("/")[:-1])
        apiPath = f'{apiSubPath}/{customer_id}/devices'
        resp = conn.command(apiMethod="PUT",
                            apiPath=apiPath)
        if resp['code'] == 200:
            log_message = 'Successfully unassigned all devices from customer' \
                f' with customer id {customer_id}'
            logger.info(log_message)
        return resp

    def get_msp_devices_and_subscriptions(
            self,
            conn,
            offset=0,
            limit=10,
            device_allocation_status=0,
            device_type=None,
            customer_name=None):
        """This function fetches the list of devices & licenses under the MSP\
            account based on the provided parameters.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param offset: Pagination start index, defaults to 0
        :type offset: int, optional
        :param limit: Pagination end index, defaults to 100
        :type limit: int, optional
        :param device_allocation_status: Filter on device_allocation_status.\
            This parameter accepts the following values - 0(All),\
            1(Allocated),2(Available). Defaults to 0. 
        :type device_allocation_status: str, optional
        :param device_type: Filter on device_type. Accepted values - iap,\
            switch, all_controller. Defaults to None. 
        :type device_type: str, optional
        :param customer_name: Name of customer, defaults to None.
        :type customer_name: str, optional
        :return: Response as provided by 'command' function in\
                    class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        apiPath = urls.MSP["DEVICES"]
        apiParams = {
            "offset": offset,
            "limit": limit,
            "device_allocation_status": device_allocation_status
        }
        if device_type is not None:
            apiParams['device_type'] = device_type
        if customer_name is not None:
            apiParams['customer_name'] = customer_name

        resp = conn.command(apiMethod="GET",
                            apiPath=apiPath,
                            apiParams=apiParams)
        if resp['code'] == 200:
            log_message = 'Successfully fetched the list of devices & licenses'\
                ' based on the provided parameters'
            logger.info(log_message)
        return resp

    def get_msp_all_devices_and_subscriptions(self, conn, customer_name=None):
        """This function fetches all the devices & subscriptions from a MSP\
            account. If the customer_name parameter is passed, then it will\
            return all the devices & licenses in the customer account.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase` 
        :param customer_name: Name of customer, defaults to None. This \
            parameter will be ignored if customer_id parameter is passed
        :type customer_name: str, optional
        :return: List of device & licenses in the MSP or customer account
        :rtype: list
        """
        if customer_name is not None:
            customer_id = self.get_customer_id(
                conn, customer_name=customer_name)
            if customer_id is None:
                log_message = 'Unable to get customer_id. ' \
                    'Please provide a valid customer name'
                logger.error(log_message)
                return

        offset = 0
        limit = 50
        device_list = []
        while True:
            if customer_name:
                resp = self.get_customer_devices_and_subscriptions(
                    conn, offset=offset, limit=limit, customer_id=customer_id)
            else:
                resp = self.get_msp_devices_and_subscriptions(
                    conn, offset=offset, limit=limit)
            if resp['code'] == 200 and resp['msg']['status'] == 'success' \
                    and 'deviceList' in resp['msg']:
                resp_message = resp['msg']['deviceList']
                resp_devices = resp_message['devices']
                device_list.extend(resp_devices)
                if (len(device_list) == resp_message['total_devices']):
                    break
            else:
                logger.error(resp)
                return
            offset += limit
        return device_list

    def get_customers_per_group(self, conn, group_name, offset=0, limit=10):
        """This function fetches the list of customers to MSP group based on \
            the provided parameters.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase` 
        :param group_name: MSP group name
        :type group_name: str
        :param offset: Pagination start index, defaults to 0
        :type offset: int, optional
        :param limit: Pagination end index, defaults to 10
        :type limit: int, optional
        :return: List of device & licenses in the MSP or customer account
        :rtype: list
        """

        if group_name is None:
            logger.error("Attribute Error. Provide a valid group name.")
            return

        apiPath = f'{urls.MSP["GROUPS"]}/{group_name}/customers'
        apiParams = {
            "offset": offset,
            "limit": limit
        }
        resp = conn.command(apiMethod="GET",
                            apiPath=apiPath,
                            apiParams=apiParams)
        return resp
