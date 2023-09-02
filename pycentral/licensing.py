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

from pycentral.url_utils import urlJoin, LicensingUrl
from pycentral.base_utils import console_logger

urls = LicensingUrl()


class Subscriptions(object):
    """A python class to manage subscriptions for Aruba Central
    """

    def get_user_subscription_keys(self, conn, license_type="", offset=0,
                                   limit=100):
        """This function is used to get license subscription keys

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param license_type: Accepts basic/special, defaults to ""
        :type license_type: str, optional
        :param offset: Pagination offset, defaults to 0
        :type offset: int, optional
        :param limit: Number of subscriptions to get, defaults to 100
        :type limit: int, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["GET_KEYS"]
        params = {
            "offset": offset,
            "limit": limit
        }
        if license_type:
            params["license_type"] = license_type
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_enabled_services(self, conn):
        """This function is used to get the list of services which are enabled\
            for customer.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["GET_ENABLED_SVC"]
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def assign_device_subscription(self, conn, device_serials, services):
        """This function is used to assign subscriptions to device by\
            specifying its serial.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serials: List of serial number of device.
        :type device_serials: list
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["ASSIGN"]
        data = {
            "serials": device_serials,
            "services": services
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def unassign_device_subscription(self, conn, device_serials, services):
        """This function is used to unassign subscriptions to device by\
            specifying its serial.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param device_serials: List of serial number of device.
        :type device_serials: list
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["UNASSIGN"]
        data = {
            "serials": device_serials,
            "services": services
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def get_user_subscription_status(self, conn, license_type="all",
                                     service=""):
        """This function is used to return subscription stats.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param license_type: basic/special/all. special - will fetch the\
            statistics of special central services like presence\
            analytics(pa), ucc, clarity etc basic - will fetch the statistics\
            of device management service licenses, all - will fetch both of\
            these license types, defaults to "all"
        :type license_type: str, optional
        :param service: Service type: pa/pa,clarity etc, defaults to ""
        :type service: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["GET_STATS"]
        params = {}
        if license_type:
            params["license_type"] = license_type
        if service:
            params["service"] = service
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_services_license_config(self, conn, service_category="",
                                    device_type=""):
        """This function is used to return services configuration for\
            licensing purpose.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param service_category: Service category - dm/network, defaults to ""
        :type service_category: str, optional
        :param device_type: Device Type - iap/switch, defaults to ""
        :type device_type: str, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["GET_LIC_SVC"]
        params = {}
        if service_category:
            params["service_category"] = service_category
        if device_type:
            params["device_type"] = device_type
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def assign_subscription_all(self, conn, services):
        """This function is used to assign licenses to all devices for given\
            services. \n
        Note: This API is not applicable for MSP customer

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["ASSIGN_LIC"]
        data = {
            "services": services
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def unassign_subscription_all(self, conn, services):
        """This function is used to unassign licenses to all devices for given\
            services.\n
        Note: This API is not applicable for MSP customer

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["UNASSIGN_LIC"]
        data = {
            "services": services
        }
        resp = conn.command(apiMethod="DELETE", apiPath=path, apiData=data)
        return resp

    def assign_msp_subscription_all(self, conn, services, include_customers=[],
                                    exclude_customers=[]):
        """Assign licenses to all devices owned by tenant customers for given\
        services. If include_customers and exclude_customers parameters are\
        not provided, licenses will be assigned for all customers(MSP, \
        tenants) devices. \n
        Note: License assignment is not supported for the MSP owned devices.\
        Since it is a background job, please wait for few minutes for all\
        devices to be subscribed in case of customer having large number of\
        devices

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :param include_customers:  if provided, licenses will be assigned only\
            for the customers present in include_customers list\n
            (Exception: License assignment will be ignored for MSP owned \
            devices), default=[]
        :type include_customers: list, optional
        :param exclude_customers:  if provided, licenses will be assigned for\
            MSP/tenant customers except the customers present in\
            exclude_customers list, default=[]
        :type exclude_customers: list, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["ASSIGN_LIC_MSP"]
        data = {
            "services": services
        }
        if include_customers:
            data["include_customers"] = include_customers
        if exclude_customers:
            data["exclude_customers"] = exclude_customers
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def unassign_msp_subscription_all(self, conn, services,
                                      include_customers=[],
                                      exclude_customers=[]):
        """Remove service licenses to all devices the devices owned by tenant\
        and MSP. However license assignment is not supported for the MSP owned\
        devices but un-assignment is supported for the customers who are\
        transitioning from Non-MSP to MSP mode to release license quantity for\
        better utilization. \n

        Note: If include_customers and exclude_customers parameters are not\
        provided, licenses will be unassigned for all customers(MSP, tenants)\
        devices.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :param include_customers:  if provided, licenses will be unassigned\
            only for the customers present in include_customers list.\n
            (Exception: License assignment will be ignored for MSP owned \
            devices), default=[]
        :type include_customers: list, optional
        :param exclude_customers:  if provided, licenses will be unassigned\
            for MSP/tenant customers except the customers present in\
            exclude_customers list, default=[]
        :type exclude_customers: list, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.SUBSCRIPTIONS["UNASSIGN_LIC_MSP"]
        data = {
            "services": services
        }
        if include_customers:
            data["include_customers"] = include_customers
        if exclude_customers:
            data["exclude_customers"] = exclude_customers
        resp = conn.command(apiMethod="DELETE", apiPath=path, apiData=data)
        return resp


class AutoLicense(object):
    """A python class to manage auto-licenses for Aruba Central
    """

    def disable_autolicensing_services(self, conn, services):
        """This function is used to disable auto licensing.
        Note: This API is not applicable for MSP customer

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.AUTO_LICENSE["DISABLE_SVC"]
        data = {
            "services": services
        }
        resp = conn.command(apiMethod="DELETE", apiPath=path, apiData=data)
        return resp

    def get_autolicense_services(self, conn):
        """This function is used to get services which are auto enabled.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.AUTO_LICENSE["GET_SVC"]
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def assign_autolicense_services(self, conn, services):
        """This function is used to assign licenses to all devices for given\
            services and enable auto licensing. \n
            Note: This API is not applicable for MSP customer

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.AUTO_LICENSE["ASSIGN_LIC_SVC"]
        data = {
            "services": services
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def disable_msp_autolicense_services(self, conn, services,
                                         include_customers=[],
                                         exclude_customers=[]):
        """Disable auto license settings for MSP and Tenants for the given\
            services. This will not change the current
        license device mapping

        Note: If include_customers and exclude_customers are not provided then\
            auto license setting will be disabled
        for all customers i.e MSP and tenants.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :param include_customers: if provided, licensing will be disable only\
            for the customers present in include_customers list, defaults to []
        :type include_customers: list, optional
        :param exclude_customers: if provided, licensing will be disabled for\
            the customers except the customers present in exclude_customers\
            list, defaults to []
        :type exclude_customers: list, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.AUTO_LICENSE["DISABLE_LIC_SVC_MSP"]
        data = {
            "services": services
        }
        if include_customers:
            data["include_customers"] = include_customers
        if exclude_customers:
            data["exclude_customers"] = exclude_customers
        resp = conn.command(apiMethod="DELETE", apiPath=path, apiData=data)
        return resp

    def get_msp_autolicense_services(self, conn, customer_id: str):
        """[summary]

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param customer_id: Customer id of msp or tenant.
        :type customer_id: str
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.AUTO_LICENSE["GET_LIC_SVC_MSP"]
        params = {
            "customer_id": customer_id
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def assign_msp_autolicense_services(self, conn, services,
                                        include_customers=[],
                                        exclude_customers=[]):
        """Enable auto license settings for MSP and Tenants. Assign licenses\
        for given services to all the devices owned by tenant customers.\n
        Note - License assignment is not supported for the MSP owned devices.\
        License assignment will be in paused state if the total license tokens\
        are less than total device counts(including MSP and tenants)

        Note: If include_customers and exclude_customers are not provided then\
        license settings will be enabled for all customers i.e MSP, tenants\
        and future tenants(Note: Newly created tenant will be inherited\
        license settings from MSP)

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param services: List of service names. Call services/config API to\
            get the list of valid service names.
        :type services: list
        :param include_customers: if provided, license settings will be\
            enabled only for the customers present
            in include_customers list., defaults to []
        :type include_customers: list, optional
        :param exclude_customers: if provided, license settings will be\
            enabled for customers except the customers present in\
            exclude_customers list, defaults to []
        :type exclude_customers: list, optional
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.AUTO_LICENSE["ASSIGN_LIC_SVC_MSP"]
        data = {
            "services": services
        }
        if include_customers:
            data["include_customers"] = include_customers
        if exclude_customers:
            data["exclude_customers"] = exclude_customers
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def get_license_status(self, conn, service_name: str):
        """Get services and corresponding license token availability status.\
        If True, license tokens are more than device count else less than\
        device count.(Note - Autolicense is in paused state when license\
        tokens are less than device count)

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param service_name: Specific service name(dm/pa/..). Call\
            services/config API to get the list of valid service names.
        :type service_name: str
        :return: Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(
            urls.AUTO_LICENSE["GET_SVC_LIC_TOK"],
            service_name,
            "status")
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp
