# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils import GLP_URLS, generate_url
from .subscriptions import Subscriptions
from ..utils.glp_utils import check_progress, rate_limit_check
import time

DEVICE_GET_LIMIT = 2000
# Input size per request for DEVICE module APIs.
INPUT_SIZE = 5
# Rate limit for PATCH Device functions.
PATCH_RPM = 5
# Rate limit for POST Device functions.
POST_RPM = 4


class Devices(object):
    def get_all_devices(self, conn, select=None):
        """Get a list of devices managed in a workspace.

        Args:
            conn (NewCentralBase): pycentral base connection object
            select (list, optional): A comma separated list of select properties to display in
                the response. The default is that all properties are returned.
                Example: select=serialNumber,macAddress

        Returns:
            (list[dict]): A list of all devices in the workspace, or an empty list if an error occurs
        """
        conn.logger.info("Getting all devices in GLP workspace")
        limit = DEVICE_GET_LIMIT
        offset = 0
        device_list = []

        while True:
            resp = self.get_device(
                conn, limit=limit, offset=offset, select=select
            )
            if resp["code"] != 200:
                conn.logger.error(
                    f"Error fetching list of devices: {resp['code']} - {resp['msg']}"
                )
                device_list = []
                break
            device_resp_message = resp["msg"]
            device_list.extend(device_resp_message["items"])
            if len(device_list) == device_resp_message["total"]:
                conn.logger.info(
                    f"Total devices fetched from account: {len(device_list)}"
                )
                break
            offset += DEVICE_GET_LIMIT
        return device_list

    def get_device(
        self,
        conn,
        limit=DEVICE_GET_LIMIT,
        offset=0,
        filter=None,
        select=None,
        sort=None,
    ):
        """Get a list of devices managed in a GLP workspace from filter/select and sort inputs.

        Rate limits are enforced on this API. 160 requests per minute is supported per workspace.
        API will result in 429 if this threshold is breached.

        Args:
            conn (NewCentralBase): pycentral base connection object
            limit (int, optional): Specifies the number of results to be returned.
                The default value is 2000
            offset (int, optional): Specifies the zero-based resource offset to start the
                response from. The default value is 0
            filter (str, optional): Device filters joined by logical operators
            select (list, optional): Properties of devices to be displayed in response
            sort (str, optional): Sort string expressions

        Returns:
            (dict): Response as provided by 'command' function in NewCentralBase
        """

        conn.logger.info("Getting a device in GLP workspace")
        path = generate_url(GLP_URLS["DEVICE"], category="devices")

        params = {"limit": limit, "offset": offset}
        if filter:
            params["filter"] = filter
        if select:
            params["select"] = select
        if sort:
            params["sort"] = sort

        resp = conn.command("GET", path, "glp", api_params=params)
        if resp["code"] == 200:
            conn.logger.info("Get device successful!")
        else:
            conn.logger.error("Get device failed!")
        return resp

    def get_device_id(self, conn, serial):
        """Get device ID in a GLP workspace based on serial number.

        Args:
            conn (NewCentralBase): pycentral base connection object
            serial (str): Device serial number

        Returns:
            (tuple(bool, str)): Tuple of two elements. First element returns True if device id
                is found, else False. The second element is a GLP device ID if found, else an
                error message from the response
        """

        filter = f"serialNumber eq '{serial}'"
        resp = self.get_device(conn, filter=filter)
        if resp["code"] != 200:
            return (resp, (False, "Bad request for get_id"))
        elif resp["msg"]["count"] == 0:
            return (False, "Serial not found")
        else:
            return (True, resp["msg"]["items"][0]["id"])

    def get_status(self, conn, id):
        """Get status of an async GLP devices request.

        Args:
            conn (NewCentralBase): pycentral base connection object
            id (str): Transaction ID from async API request

        Returns:
            (dict): Response as provided by 'command' function in NewCentralBase
        """

        path = generate_url(f"{GLP_URLS['ASYNC']}/{id}", category="devices")
        resp = conn.command("GET", path, "glp")
        return resp

    def add_devices(self, conn, network=[], compute=[], storage=[]):
        """Add devices to a workspace in GreenLake Platform (GLP).

        Handles coordinating chaining requests if passed more than 5 devices (max per api call).
        Can use any combination of network, compute, and storage devices. Always returns a 202
        response code if basic input validation is met. Currently does not support Async get
        status handling to confirm operation success.

        Args:
            conn (NewCentralBase): pycentral base connection object
            network (list, optional): Network devices as dict objects
            compute (list, optional): Compute devices as dict objects
            storage (list, optional): Storage devices as dict objects

        Returns:
            (list[dict]): List of response objects as provided by 'command' function in NewCentralBase
        """

        count = len(network) + len(compute) + len(storage)
        resp_list = []

        # Check for rate limit handler
        if count > INPUT_SIZE:
            conn.logger.info("WARNING MORE THAN 5 DEVICES IS AN ALPHA FEATURE!")
            for device_type, device_list in (
                ("network", network),
                ("compute", compute),
                ("storage", storage),
            ):
                if device_list:
                    resp_list.append(
                        self.__add_dev(conn, device_type, device_list)
                    )
            return resp_list
        else:
            path = generate_url(GLP_URLS["DEVICE"], category="devices")
            data = {"network": network, "compute": compute, "storage": storage}
            resp = conn.command("POST", path, "glp", api_data=data)
            resp_list.append(resp)
            if resp["code"] == 202:
                conn.logger.info("Add device request accepted...")
            else:
                conn.logger.error("Add device request failed!")
            return resp_list

    def __add_dev(self, conn, type, inputs):
        """Helper function for add_devices.

        Handles splitting inputs larger than input size and coordinates running the commands
        to not exceed rate limit.

        Args:
            conn (NewCentralBase): pycentral base connection object
            type (str): One of network, compute, or storage
            inputs (list): List of 'type' objects in dict format

        Returns:
            (list[dict]): Response object(s) as provided by 'command' function in NewCentralBase
        """

        path = generate_url(GLP_URLS["DEVICE"], category="devices")
        data = {"network": [], "compute": [], "storage": []}

        if len(inputs) > INPUT_SIZE:
            split_input, wait_time = rate_limit_check(
                inputs, INPUT_SIZE, POST_RPM
            )

            resp_list = []

            for devices in split_input:
                data["network"] = devices if type == "network" else []
                data["compute"] = devices if type == "compute" else []
                data["storage"] = devices if type == "storage" else []
                resp = conn.command("POST", path, "glp", api_data=data)
                if resp["code"] != 202:
                    conn.logger.error(
                        f"Add device request failed for {inputs}!"
                    )
                else:
                    conn.logger.info("Add device request accepted...")
                resp_list.append(resp)
                time.sleep(wait_time)
            return resp_list
        else:
            data["network"] = inputs if type == "network" else []
            data["compute"] = inputs if type == "compute" else []
            data["storage"] = inputs if type == "storage" else []

            resp = conn.command("POST", path, "glp", api_data=data)
            if resp["code"] != 202:
                conn.logger.error(f"Add device request failed for {inputs}!")
            else:
                conn.logger.info("Add device request accepted...")
            time.sleep(60 / POST_RPM)
            return resp

    def add_sub(self, conn, devices, sub, serial=False, key=False):
        """Add subscription to device(s).

        API endpoint supports five devices per request. Handles chaining multiple requests for
        greater than five devices supplied. An additional response dict object will be appended
        to the return list for each additional request required to handle the number of input
        devices passed to the function.

        Args:
            conn (NewCentralBase): pycentral base connection object
            devices (list): List of device id(s) or serial numbers
            sub (str): Subscription id or key
            serial (bool, optional): Flag to use device serial numbers, default is False
            key (bool, optional): Flag to use subscription key, default is False

        Returns:
            (list[dict]): List of API response objects as provided by 'command' function in NewCentralBase
        """

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        if key:
            s = Subscriptions()
            id = s.get_sub_id(conn, sub)
            if id[0]:
                sub = id[1]
            else:
                conn.logger.error("Get sub ID from key failed!")

        split_input, wait_time = None, None

        # Split devices list per input size.
        if len(devices) > INPUT_SIZE:
            split_input, wait_time = rate_limit_check(
                devices, INPUT_SIZE, PATCH_RPM
            )
            conn.logger.info("WARNING MORE THAN 5 DEVICES IS A BETA FEATURE!")

        # Setup variables for iterating commands.
        queue = [devices] if not split_input else split_input
        resp_list = []
        path = generate_url(GLP_URLS["DEVICE"], category="devices")
        body = {"subscription": [{"id": sub}]}

        for inputs in queue:
            params = {"id": inputs}

            resp = conn.command(
                "PATCH", path, "glp", api_params=params, api_data=body
            )
            if resp["code"] == 202:
                conn.logger.info("Add sub request accepted...")
                id = resp["msg"]["transactionId"]
                status = check_progress(conn, id, self, limit=PATCH_RPM)
                if status[0]:
                    conn.logger.info(
                        "Sucessfully added subscriptions to devices!"
                    )
                    resp_list.append(status[1])
                else:
                    conn.logger.error("Add subscription failed!")
                    resp_list.append(status[1])
            else:
                conn.logger.error("Bad request for add subscription!")
                resp_list.append(resp)

            if wait_time:
                time.sleep(wait_time)

        return resp_list

    def remove_sub(self, conn, devices, serial=False):
        """Remove a subscription from a device.

        API endpoint supports five devices per request. Handles chaining multiple requests for
        greater than five devices supplied. An additional response dict object will be appended
        to the return list for each additional request required to handle the number of input
        devices passed to the function.

        Args:
            conn (NewCentralBase): pycentral base connection object
            devices (list): List of device id(s) or serial numbers
            serial (bool, optional): Flag to use device serial numbers, default is False

        Returns:
            (list[dict]): List of API response objects as provided by 'command' function in NewCentralBase
        """

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        split_input, wait_time = None, None

        # Split devices list per input size.
        if len(devices) > INPUT_SIZE:
            split_input, wait_time = rate_limit_check(
                devices, INPUT_SIZE, PATCH_RPM
            )
            conn.logger.info("WARNING MORE THAN 5 DEVICES IS A BETA FEATURE!")

        # Setup variables for iterating commands.
        queue = [devices] if not split_input else split_input
        resp_list = []
        path = generate_url(GLP_URLS["DEVICE"], category="devices")
        body = {"subscription": []}

        for inputs in queue:
            params = {"id": inputs}

            resp = conn.command(
                "PATCH", path, "glp", api_params=params, api_data=body
            )
            if resp["code"] == 202:
                conn.logger.info("Remove sub request accepted...")
                id = resp["msg"]["transactionId"]
                status = check_progress(conn, id, self, limit=PATCH_RPM)
                if status[0]:
                    conn.logger.info(
                        "Sucessfully Removed subscriptions from devices!"
                    )
                    resp_list.append(status[1])
                else:
                    conn.logger.error("Remove subscription failed!")
                    resp_list.append(status[1])
            else:
                conn.logger.error("Bad request for remove subscription!")
                resp_list.append(resp)

            if wait_time:
                time.sleep(wait_time)

        return resp_list

    def assign_devices(
        self, conn, devices=None, application=None, region=None, serial=False
    ):
        """Assign devices to an application by passing one or more device id(s) or serial numbers.

        Currently supports assigning and un-assigning devices to and from an application or
        applying/removing subscriptions to/from devices. Rate limits are enforced on this API.
        Five requests per minute is supported per workspace. API will result in 429 if this
        threshold is breached.

        Args:
            conn (NewCentralBase): pycentral base connection object
            devices (list, optional):  List of device id(s) or serial numbers
            application (str, optional): Application id
            region (str, optional): AHE region of the application the device is provisioned in
            serial (bool, optional): Flag to use device serial numbers, default is False

        Returns:
            (dict): API response
        """

        conn.logger.info("Assigning device(s) to an application")
        path = generate_url(GLP_URLS["DEVICE"], category="devices")

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        if len(devices) > INPUT_SIZE:
            resp = []
            rate_check = rate_limit_check(devices, INPUT_SIZE, PATCH_RPM)
            queue, wait_time = rate_check

            for i in range(len(queue)):
                params = {"id": queue[i]}

                data = {"application": {"id": application}, "region": region}

                time.sleep(wait_time)

                resp.append(
                    conn.command(
                        api_method="PATCH",
                        api_path=path,
                        api_params=params,
                        api_data=data,
                        app_name="glp",
                    )
                )

        else:
            params = {"id": devices}

            data = {"application": {"id": application}, "region": region}

            resp = conn.command(
                api_method="PATCH",
                api_path=path,
                api_params=params,
                api_data=data,
                app_name="glp",
            )

        if resp["code"] == 202:
            conn.logger.info(
                "Assign device(s) to application request accepted..."
            )
            id = resp["msg"]["transactionId"]
            status = check_progress(conn, id, self, limit=PATCH_RPM)
            if status[0]:
                conn.logger.info(
                    "Sucessfully assigned device(s) to application!"
                )
                return status[1]
            else:
                conn.logger.error("Assign device(s) to application failed!")
                return status[1]
        conn.logger.error("Bad request for assign device(s) to application!")
        return resp

    def unassign_devices(self, conn, devices=None, serial=False):
        """Unassign devices from an application by passing one or more device id(s) or serial numbers.

        Currently supports assigning and un-assigning devices to and from an application or
        applying/removing subscriptions to/from devices. Rate limits are enforced on this API.
        Five requests per minute is supported per workspace. API will result in 429 if this
        threshold is breached.

        Args:
            conn (NewCentralBase): pycentral base connection object
            devices (list, optional): List of device id(s) or serial numbers
            serial (bool, optional): Flag to use device serial numbers, default is False

        Returns:
            (dict): API response
        """

        conn.logger.info("Unassigning device(s) from an application")
        path = generate_url(GLP_URLS["DEVICE"], category="devices")

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        if len(devices) > INPUT_SIZE:
            resp = []
            rate_check = rate_limit_check(devices, INPUT_SIZE, PATCH_RPM)
            queue, wait_time = rate_check

            for i in range(len(queue)):
                params = {"id": queue[i]}

                data = {"application": {"id": None}, "region": None}

                time.sleep(wait_time)

                resp.append(
                    conn.command(
                        api_method="PATCH",
                        api_path=path,
                        api_params=params,
                        api_data=data,
                        app_name="glp",
                    )
                )

        else:
            params = {"id": devices}

            data = {"application": {"id": None}, "region": None}

            resp = conn.command(
                api_method="PATCH",
                api_path=path,
                api_params=params,
                api_data=data,
                app_name="glp",
            )

        if resp["code"] == 202:
            conn.logger.info("Unassign device(s) from application accepted...")
            id = resp["msg"]["transactionId"]
            status = check_progress(conn, id, self, limit=PATCH_RPM)
            if status[0]:
                conn.logger.info(
                    "Sucessfully unassigned device(s) from application!"
                )
                return status[1]
            else:
                conn.logger.error("Unassign device(s) from application failed!")
                return status[1]
        conn.logger.error(
            "Bad request for unassign device(s) from application!"
        )
        return resp
