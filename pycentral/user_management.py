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

from pycentral.url_utils import UserManagementUrl, urlJoin
from pycentral.base_utils import console_logger

urls = UserManagementUrl()


class Users(object):
    """A Python class to manage Aruba Central Users via REST APIs.
    """

    def list_users(self, conn, limit=20, offset=0, sort="+timestamp",
                   email=None):
        """(This API will be deprecated in future release). Use get_users().
        Returns all users from the system associated to user's account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param limit: Maximum number of items to return, defaults to 20
        :type limit: int, optional
        :param offset: Zero based offset to start from, defaults to 0
        :type offset: int, optional
        :param sort: Sort ordering. One if +timestamp/-timestamp/+username/\
            -username, defaults to "+timestamp"
        :type sort: str, optional
        :param email: Filter users by email, defaults to None
        :type email: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.USERS["LIST"]
        params = {
            "limit": limit,
            "offset": offset,
            "sort": sort
        }
        if email:
            params["email"] = email

        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_users(self, conn, limit=20, offset=0, order_by="+username",
                  app_name=None, user_type=None, status=None):
        """Returns all users from the system associated to user's account

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param limit: Maximum number of items to return, defaults to 20
        :type limit: int, optional
        :param offset: Zero based offset to start from, defaults to 0
        :type offset: int, optional
        :param order_by: Sort ordering (ascending or descending). +username\
            signifies ascending order of username., defaults to "+username"
        :type order_by: str, optional
        :param app_name: Filter users based on app_name, defaults to None
        :type app_name: str, optional
        :param user_type: Filter based on system or federated user, defaults\
            to None
        :type user_type: str, optional
        :param status: Filter user based on status (inprogress, failed),\
            defaults to None
        :type status: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.USERS["GET_USERS"]
        params = {
            "offset": offset,
            "limit": limit,
            "order_by": order_by
        }
        if app_name:
            params["app_name"] = app_name
        if user_type:
            params["type"] = user_type
        if status:
            params["status"] = status

        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def get_user(self, conn, username, system_user=True):
        """Get user account details specified by user email

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param username: User's email id is specified as the user id
        :type username: str
        :param system_user: false if federated user, defaults to True
        :type system_user: bool, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.USERS["GET"], username)
        params = {
            "system_user": system_user
        }
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def _build_user(self, username, description, name, phone, address,
                    applications, password=None):
        """Internal function to build the JSON payload which is required to\
        create/update users.

        :param username: User's email id is specified as the user id
        :type username: str
        :param description: description of user
        :type description: str
        :param name: A dict containing 'firstname' and 'lastname' key value\
            pairs.
        :type name: dict
        :param phone: Phone number. Format: +country_code-local_number
        :type phone: str
        :param address: Address of the user in dict format containing\
            'street', 'city', 'state', 'country' and 'zipcode'.
        :type address: dict
        :param applications: List of dictionaries. Each element containing a\
            dict to represent 'name', and 'info' of the application for which\
            the user will be granted access. 'info' is a dict with 'role', \
            'tenant_role' and 'scope' keys. With 'scope' containing 'groups'\
            key with value as a list of groups.
        :type applications: list
        :param password: password of user account, defaults to None
        :type password: str, optional
        :return: Constructed paylod in dict format to be used for POST/PATCH\
            of rbac user account.
        :rtype: dict
        """
        payload = {
            "username": username,
            "description": description,
            "name": name,
            "phone": phone,
            "address": address,
            "applications": applications
        }
        if password:
            payload["password"] = password
        return payload

    def create_user(self, conn, username: str, password: str, description: str,
                    name: dict, phone: str, address: dict, applications: dict):
        """Create a user account. For public cloud environment, user has to\
        re-register via invitation email. Email will be sent during processing\
        of this request. Providing role on account setting app is mandatory in\
        this API along with other subscribed apps. Scope must be given only\
        for NMS app. For non-nms apps such as account setting refer the\
        parameters in the example json payload.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param username: User's email id is specified as the user id
        :type username: str
        :param password: password of user account, defaults to None
        :type password: str
        :param description: description of user
        :type description: str
        :param name: 'firstname' and 'lastname' of the user.
        :type name: dict
        :param phone: Phone number. Format: +country_code-local_number
        :type phone: str
        :param address: Address of the user. Dict containing 'street', 'city',\
            'state', 'country' and 'zipcode'.
        :type address: dict
        :param applications: Define applications that needs access. \n
            * keyword name: Name of the application. Example: 'nms',\
                'account_setting', etc. \n
            * keyword info:  A list of dictionaries. Each element containing\
                'role', 'tenant_role', and 'scope'. Where 'scope' contains\
                'groups' key with list of groups. \n
        :type applications: dict
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.USERS["CREATE"]
        data = self._build_user(
            username,
            description,
            name,
            phone,
            address,
            applications,
            password)
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def update_user(self, conn, username: str, description: str,
                    name: dict, phone: str, address: dict, applications: dict):
        """Update user account details specified by user id. Providing info on\
        account setting app is mandatory in this API along with other\
        subscribed apps.Scope must be given only for NMS app. For non-nms apps\
        such as account setting refer the parameters in the example json\
        payload.

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param username: User's email id is specified as the user id
        :type username: str
        :param description: description of user
        :type description: str
        :param name: 'firstname' and 'lastname' of the user.
        :type name: dict
        :param phone: Phone number. Format: +country_code-local_number
        :type phone: str
        :param address: Address of the user. Dict containing 'street', 'city',\
            'state', 'country' and 'zipcode'.
        :type address: dict
        :param applications: Define applications that needs access. \n
            * keyword name: Name of the application. Example: 'nms',\
                'account_setting', etc. \n
            * keyword info:  A list of dictionaries. Each element containing\
                'role', 'tenant_role', and 'scope'. Where 'scope' contains\
                'groups' key with list of groups. \n
        :type applications: dict
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.USERS["UPDATE"], username)
        data = self._build_user(
            username,
            description,
            name,
            phone,
            address,
            applications)
        resp = conn.command(apiMethod="PATCH", apiPath=path, apiData=data)
        return resp

    def delete_user(self, conn, username, system_user=True):
        """Delete user account details specified by user id

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param username: User's email id is specified as the user id
        :type username: str
        :param system_user: false if federated user, defaults to True
        :type system_user: bool, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.USERS["DELETE"], username)
        params = {
            "system_user": system_user
        }
        resp = conn.command(apiMethod="DELETE", apiPath=path, apiParams=params)
        return resp


class Roles(object):
    """A Python class to manage Aruba Central User Roles via REST APIs.
    """

    def get_user_roles(self, conn, app_name=None, limit=20, offset=0,
                       order_by="+rolename"):
        """Get list of all roles

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param app_name: Filter users based on app_name, defaults to None
        :type app_name: str, optional
        :param limit: Maximum number of items to return, defaults to 20
        :type limit: int, optional
        :param offset: Zero based offset to start from, defaults to 0
        :type offset: int, optional
        :param order_by: Sort ordering. +rolename means ascending order of\
            rolename, defaults to "+rolename"
        :type order_by: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urls.ROLES["GET_ROLES"]
        params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by
        }
        if app_name:
            params["app_name"] = app_name
        resp = conn.command(apiMethod="GET", apiPath=path, apiParams=params)
        return resp

    def create_user_role(self, conn, app_name, rolename, applications,
                         permission="modify"):
        """Create an user role in an app

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param app_name: app name where role needs to be created
        :type app_name: str
        :param rolename: name of the role
        :type rolename: str
        :param applications: List of dict. Each element containing the\
            following structure. \n
            * keyword appname: Name of the application. Example: 'nms',\
                'account_setting', etc. \n
            * keyword modules:  A list of dictionaries. Each element\
                containing 'module_name'
                and 'permission' for the modules. \n
            * keyword permission: permission for the app \n
        :type applications: dict
        :param permission: permission of the role, defaults to "modify"
        :type permission: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.ROLES["CREATE"], app_name, "roles")
        data = {
            "rolename": rolename,
            "permission": permission,
            "applications": applications
        }
        resp = conn.command(apiMethod="POST", apiPath=path, apiData=data)
        return resp

    def delete_user_role(self, conn, app_name, rolename):
        """Delete a role specified by role name

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param app_name: app name
        :type app_name: str
        :param rolename: User role name
        :type rolename: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.ROLES["DELETE"], app_name, "roles", rolename)
        resp = conn.command(apiMethod="DELETE", apiPath=path)
        return resp

    def get_user_role(self, conn, app_name, rolename):
        """Get Role details

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
             API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param app_name: app name
        :type app_name: str
        :param rolename: User role name
        :type rolename: str
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.ROLES["GET"], app_name, "roles", rolename)
        resp = conn.command(apiMethod="GET", apiPath=path)
        return resp

    def update_user_role(
            self,
            conn,
            app_name,
            rolename,
            applications,
            permission="modify"):
        """Update a role specified by role name

        :param conn: Instance of class:`pycentral.ArubaCentralBase` to make an\
            API call.
        :type conn: class:`pycentral.ArubaCentralBase`
        :param app_name: app name
        :type app_name: str
        :param rolename: User role name
        :type rolename: str
        :param applications: List of dict. Each element containing the\
            following structure. \n
            * keyword appname: Name of the application. Example: 'nms',\
                'account_setting', etc. \n
            * keyword modules:  A list of dictionaries. Each element\
                containing 'module_name' and 'permission' for the modules. \n
            * keyword permission: permission for the app \n
        :type applications: dict
        :param permission: [description], defaults to "modify"
        :type permission: str, optional
        :return: HTTP Response as provided by 'command' function in\
            class:`pycentral.ArubaCentralBase`
        :rtype: dict
        """
        path = urlJoin(urls.ROLES["GET"], app_name, "roles", rolename)
        data = {
            "rolename": rolename,
            "permission": permission,
            "applications": applications
        }
        resp = conn.command(apiMethod="PATCH", apiPath=path, apiData=data)
        return resp
