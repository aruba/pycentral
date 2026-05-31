from ..utils.url_utils import generate_url
import time
from ..exceptions import ParameterError
from ..utils.monitoring_utils import build_timestamp_filter
from ..utils.troubleshooting_utils import (
    SUPPORTED_DEVICE_TYPES,
    TROUBLESHOOTING_METHOD_DEVICE_MAPPING,
)


class Troubleshooting:
    @staticmethod
    def aaa_aps_test(
        central_conn,
        serial_number,
        radius_server_ip,
        username,
        password,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a AAA test on the specified AP device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            radius_server_ip (str): RADIUS server IP address or hostname.
            username (str): Username for authentication.
            password (str): Password for authentication.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If initiating the AAA test fails.
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("aaa_test"),
        )

        try:
            response = Troubleshooting.initiate_aaa_aps_test(
                central_conn=central_conn,
                serial_number=serial_number,
                radius_server_ip=radius_server_ip,
                username=username,
                password=password,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_aaa_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating AAA test for {device_type} {serial_number} on {radius_server_ip}: {str(e)}"
            )
            raise

    @staticmethod
    def aaa_cx_test(
        central_conn,
        serial_number,
        radius_server_ip,
        username,
        password,
        auth_method_type,
        radius_server_port=None,
        vrf=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a AAA test on the specified CX device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            radius_server_ip (str): RADIUS server IP address or hostname.
            username (str): Username for authentication.
            password (str): Password for authentication.
            auth_method_type (str): Authentication method type, 'chap' or 'pap'.
            radius_server_port (int, optional): RADIUS server port.
            vrf (str, optional): VRF name.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If initiating the AAA test fails.
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("aaa_test"),
        )

        try:
            response = Troubleshooting.initiate_aaa_cx_test(
                central_conn=central_conn,
                serial_number=serial_number,
                auth_method_type=auth_method_type,
                radius_server_ip=radius_server_ip,
                username=username,
                password=password,
                radius_server_port=radius_server_port,
                vrf=vrf,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_aaa_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating AAA test for {device_type} {serial_number} on {radius_server_ip}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_aaa_aps_test(
        central_conn,
        serial_number,
        radius_server_ip,
        username,
        password,
    ):
        """Initiates a AAA test on the specified AP device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            radius_server_ip (str): RADIUS server IP address or hostname.
            username (str): Username for authentication.
            password (str): Password for authentication.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If radius_server_ip is not a valid string.
            ParameterError: If username is not a valid string.
            ParameterError: If password is not a valid string.
            Exception: If initiating the AAA test fails.
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if not radius_server_ip or not isinstance(radius_server_ip, str):
            raise ParameterError(
                "RADIUS server must be a valid string IP address or hostname."
            )
        elif radius_server_ip:
            api_data["serverName"] = radius_server_ip

        if not username or not isinstance(username, str):
            raise ParameterError("Username must be a valid string.")
        elif username:
            api_data["username"] = username

        if not password or not isinstance(password, str):
            raise ParameterError("Password must be a valid string.")
        elif password:
            api_data["password"] = password

        api_path = generate_url(
            f"{device_type}/{serial_number}/aaa", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate AAA test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"AAA test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_aaa_cx_test(
        central_conn,
        serial_number,
        auth_method_type,
        radius_server_ip,
        username,
        password,
        radius_server_port=None,
        vrf=None,
    ):
        """Initiates a AAA test on the specified CX device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            auth_method_type (str): Authentication method type, 'chap' or 'pap'.
            radius_server_ip (str): RADIUS server IP address or hostname.
            username (str): Username for authentication.
            password (str): Password for authentication.
            radius_server_port (int, optional): RADIUS server port.
            vrf (str, optional): VRF name.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If auth_method_type is not 'chap' or 'pap'.
            ParameterError: If radius_server_ip is not a valid string.
            ParameterError: If username is not a valid string.
            ParameterError: If password is not a valid string.
            ParameterError: If radius_server_port is not a valid integer between 1-65535.
            ParameterError: If vrf is not a valid string.
            Exception: If initiating the AAA test fails.
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if (
            not auth_method_type
            or not isinstance(auth_method_type, str)
            or auth_method_type.lower() not in ["chap", "pap"]
        ):
            raise ParameterError(
                "Authentication method type must be 'chap' or 'pap'."
            )
        elif auth_method_type:
            api_data["authMethodType"] = auth_method_type

        if not radius_server_ip or not isinstance(radius_server_ip, str):
            raise ParameterError(
                "RADIUS server IP address must be a valid string."
            )
        elif radius_server_ip:
            api_data["radiusServerIp"] = radius_server_ip

        if not username or not isinstance(username, str):
            raise ParameterError("Username must be a valid string.")
        elif username:
            api_data["username"] = username

        if not password or not isinstance(password, str):
            raise ParameterError("Password must be a valid string.")
        elif password:
            api_data["password"] = password

        if (
            radius_server_port
            and not isinstance(radius_server_port, int)
            or (
                isinstance(radius_server_port, int)
                and not (1 <= radius_server_port <= 65535)
            )
        ):
            raise ParameterError(
                "Radius server port must be a valid integer between 1 to 65535."
            )
        elif radius_server_port:
            api_data["radiusServerPort"] = radius_server_port

        if vrf and not isinstance(vrf, str):
            raise ParameterError("VRF must be a valid string.")
        elif vrf:
            api_data["vrf"] = vrf

        api_path = generate_url(
            f"{device_type}/{serial_number}/aaa", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate AAA test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"AAA test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_aaa_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """Retrieves the results of an AAA test on the specified device with the provided task ID.

        Supported device type includes AP and CX.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aps' or 'cx').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If retrieving the test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/aaa/async-operations/{task_id}",
                "troubleshooting",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get AAA result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"AAA for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"AAA for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def cable_test(
        central_conn,
        device_type,
        serial_number,
        ports,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a cable test on the specified device and polls for test result.

        Supported device type includes AOS-S and CX.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s' or 'cx').
            serial_number (str): Serial number of the device.
            ports (list): List of the ports to test.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If initiating the cable test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
        )

        try:
            response = Troubleshooting.initiate_cable_test(
                central_conn=central_conn,
                ports=ports,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_cable_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating cable test for {device_type} {serial_number} on {ports}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_cable_test(
        central_conn,
        device_type,
        serial_number,
        ports,
    ):
        """Initiates a cable test on the specified device.

        Supported device type includes AOS-S and CX.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s' or 'cx').
            serial_number (str): Serial number of the device.
            ports (list): List of the ports to test.

        Returns:
            (dict): Response from the API containing task ID and other details

        Raises:
            ParameterError: If ports parameter is invalid.
            Exception: If initiating the cable test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
        )

        if not ports or not isinstance(ports, list):
            raise ParameterError("Ports must be a non-empty list.")

        api_data = {"ports": ports}

        api_path = generate_url(
            f"{device_type}/{serial_number}/cableTest", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate cable test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Cable test initiated successfully for {device_type}"
            f" {serial_number} on {ports}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_cable_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """Retrieves the results of a cable test on the specified device.

        Supported device type includes AOS-S and CX.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aos-s' or 'cx').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API

        Raises:
            Exception: If retrieving the cable test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/cableTest/async-operations/{task_id}",
                "troubleshooting",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get cable test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Cable test for {device_type} {serial_number} with task ID"
                f" {task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Cable test for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def disconnect_all_clients(central_conn, device_type, serial_number):
        """Disconnects all clients from the specified device.

        Supported device type includes GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the API.

        Raises:
            Exception: If initiating the disconnect fails.
        """

        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_all_clients"
            ),
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/disconnectClientAll",
                "troubleshooting",
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                "Failed to initiate disconnect for all clients: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            "Disconnect all clients initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_all_users(central_conn, device_type, serial_number):
        """Disconnects all users from the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the API.

        Raises:
            Exception: If initiating the disconnect fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_all_users"
            ),
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/disconnectUserAll",
                "troubleshooting",
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                "Failed to initiate disconnect for all users: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            "Disconnect all users initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_all_users_ssid(
        central_conn, device_type, serial_number, network
    ):
        """Disconnects all users from the specified device on the specified
        network/SSID.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            network (str): SSID of the network to disconnect users from.

        Returns:
            (dict): Response from the API.

        Raises:
            ParameterError: If network parameter is invalid.
            Exception: If initiating the disconnect fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_all_users_ssid"
            ),
        )

        api_data = dict()
        if not isinstance(network, str):
            raise ParameterError("SSID must be a valid string.")
        else:
            api_data["networkName"] = network

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/disconnectUserByNetwork",
                "troubleshooting",
            ),
            api_data=api_data,
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate disconnect for all users on SSID {network}: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Disconnect all users on SSID {network} initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_client_mac_addr(
        central_conn, device_type, serial_number, mac_address
    ):
        """Disconnects a client from the specified device by MAC address.

        Supported device type includes GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('gateways').
            serial_number (str): Serial number of the device.
            mac_address (str): MAC address of the client to disconnect.

        Returns:
            (dict): Response from the API.

        Raises:
            Exception: If initiating the disconnect fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_client_mac_addr"
            ),
        )

        api_data = dict()

        if not isinstance(mac_address, str):
            raise ParameterError("MAC address must be a valid string.")
        else:
            api_data["clientMacAddress"] = mac_address

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/disconnectClientByMacAddress",
                "troubleshooting",
            ),
            api_data=api_data,
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate disconnect for mac {mac_address}: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Disconnect client {mac_address} initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_user_mac_addr(
        central_conn, device_type, serial_number, mac_address
    ):
        """Disconnects a user from the specified device by MAC address.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            mac_address (str): MAC address of the user to disconnect.

        Returns:
            (dict): Response from the API.

        Raises:
            ParameterError: If MAC address parameter is invalid.
            Exception: If initiating the disconnect fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_user_mac_addr"
            ),
        )

        api_data = dict()

        if not isinstance(mac_address, str):
            raise ParameterError("MAC address must be a valid string.")
        else:
            api_data["userMacAddress"] = mac_address

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/disconnectUserByMacAddress",
                "troubleshooting",
            ),
            api_data=api_data,
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate disconnect for mac {mac_address}: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Disconnect user {mac_address} initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def http_test(
        central_conn,
        device_type,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a HTTP test on the specified device and polls for test result.

        Supported device types include AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            vrf (str, optional): CX only, VRF to use. If None, default VRF will be used.
            source_interface (str, optional): CX only, source interface for the test.
            source_port (int, optional): CX only, source port for the test (0-65535).
            name_server (str, optional): CX only, IPv4 address of the DNS server to use.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If initiating the HTTP test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("http_test"),
        )

        try:
            response = Troubleshooting.initiate_http_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                destination=destination,
                vrf=vrf,
                source_interface=source_interface,
                source_port=source_port,
                name_server=name_server,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_http_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTP test for {device_type} {serial_number}"
                f" on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_http_test(
        central_conn,
        device_type,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
    ):
        """Initiates a HTTP test on the specified device.

        Supported device type includes AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            vrf (str, optional): CX only, VRF to use. If None, default VRF will be used.
            source_interface (str, optional): CX only, source interface for the test.
            source_port (int, optional): CX only, source port for the test (0-65535).
            name_server (str, optional): CX only, IPv4 address of the DNS server to use.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If vrf is not a valid string.
            ParameterError: If source_interface is not a valid string.
            ParameterError: If source_port is not a valid integer between 0-65535.
            ParameterError: If name_server is not a valid string.
            Exception: If initiating the HTTP test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("http_test"),
        )

        api_data = dict()

        if destination and isinstance(destination, str):
            # SWITCH require different key than ACCESS_POINT and GATEWAYS
            if device_type.lower() in ["aps", "gateways"]:
                api_data["url"] = destination
            else:
                api_data["destination"] = destination
                api_data["protocol"] = "HTTP"
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if vrf and not isinstance(vrf, str):
            raise ParameterError("VRF must be a valid string.")
        elif vrf:
            api_data["vrf"] = vrf

        if source_interface and not isinstance(source_interface, str):
            raise ParameterError("Source interface must be a valid string.")
        elif source_interface:
            api_data["source_interface"] = source_interface

        if (
            source_port
            and isinstance(source_port, int)
            and (0 <= source_port <= 65535)
        ):
            api_data["source_port"] = source_port
        elif source_port:
            raise ParameterError(
                "Source port must be a valid integer 0-65535."
            )

        if name_server and not isinstance(name_server, str):
            raise ParameterError("Name server must be a valid string.")
        elif name_server:
            api_data["name_server"] = name_server

        api_path = generate_url(
            f"{device_type}/{serial_number}/http", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTP test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTP test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_http_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """Retrieves the results of a HTTP test on the specified device.

        Supported device type includes AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If retrieving the test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("http_test"),
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/http/async-operations/{task_id}",
                "troubleshooting",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get HTTP test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"HTTP test for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"HTTP test for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def https_aps_test(
        central_conn,
        serial_number,
        destination,
        timeout=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a HTTPS test on the specified AP device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            timeout (int, optional): Timeout for the test in seconds.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If initiating the HTTPS test fails.
        """
        device_type = "aps"
        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_https_aps_test(
                central_conn=central_conn,
                serial_number=serial_number,
                destination=destination,
                timeout=timeout,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_https_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTPS test for {device_type} {serial_number} on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def https_cx_test(
        central_conn,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a HTTPS test on the specified CX device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            vrf (str, optional): VRF to use. If None, default VRF will be used.
            source_interface (str, optional): Source interface for the test.
            source_port (int, optional): Source port for the test (0-65535).
            name_server (str, optional): IPv4 address of the DNS server to use.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If initiating the HTTPS test fails.
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_https_cx_test(
                central_conn=central_conn,
                serial_number=serial_number,
                destination=destination,
                vrf=vrf,
                source_interface=source_interface,
                source_port=source_port,
                name_server=name_server,
            )
            task_id = Troubleshooting._get_task_id(response)
            # CX Uses HTTP GET using Protocol HTTPS
            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_http_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTPS test for {device_type} "
                f"{serial_number} on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def https_gateways_test(
        central_conn,
        serial_number,
        destination,
        count=None,
        interval=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a HTTPS test on the specified Gateway device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            count (int, optional): Number of ping packets to send (1-10).
            interval (int, optional): Time between ping packets in seconds (1-10).
            include_raw_output (bool, optional): Whether to include raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If initiating the HTTPS test fails.
        """
        device_type = "gateways"
        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_https_gateways_test(
                central_conn=central_conn,
                serial_number=serial_number,
                destination=destination,
                count=count,
                interval=interval,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_https_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTPS test for {device_type} {serial_number} on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_https_aps_test(
        central_conn,
        serial_number,
        destination,
        timeout=None,
    ):
        """Initiates a HTTPS test on the specified AP device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            timeout (int, optional): Timeout for the test in seconds.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If timeout is not a valid integer.
            ParameterError: If destination is not a valid IP address or hostname.
            Exception: If initiating the HTTPS test fails.
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if timeout and not isinstance(timeout, int) and device_type != "aps":
            raise ParameterError(
                "Timeout must be a valid integer from 1-10 and is valid "
                "for device_type=APs only."
            )
        elif timeout:
            api_data["timeout"] = timeout

        if not destination or (
            destination and not isinstance(destination, str)
        ):
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )
        elif destination:
            api_data["url"] = destination

        api_path = generate_url(
            f"{device_type}/{serial_number}/https", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTPS test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTPS test initiated successfully for {device_type} "
            f"{serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_https_cx_test(
        central_conn,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
    ):
        """Initiates a HTTPS test on the specified CX device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            vrf (str, optional): VRF to use. If None, default VRF will be used.
            source_interface (str, optional): Source interface for the test.
            source_port (int, optional): Source port for the test (0-65535).
            name_server (str, optional): IPv4 address of the DNS server to use.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If vrf is not a valid string.
            ParameterError: If source_interface is not a valid string.
            ParameterError: If source_port is not a valid integer between 0-65535.
            ParameterError: If name_server is not a valid string.
            ParameterError: If destination is not a valid IP address or hostname.
            Exception: If initiating the HTTPS test fails.
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if vrf and not isinstance(vrf, str):
            raise ParameterError("VRF must be a valid string.")
        elif vrf:
            api_data["vrf"] = vrf

        if source_interface and not isinstance(source_interface, str):
            raise ParameterError("Source interface must be a valid string.")
        elif source_interface:
            api_data["source_interface"] = source_interface

        if (
            source_port
            and isinstance(source_port, int)
            and (0 <= source_port <= 65535)
        ):
            api_data["source_port"] = source_port
        elif source_port:
            raise ParameterError(
                "Source port must be a valid integer 0-65535."
            )

        if name_server and not isinstance(name_server, str):
            raise ParameterError("Name server must be a valid string.")
        elif name_server:
            api_data["name_server"] = name_server
        if destination and isinstance(destination, str):
            api_data["destination"] = destination
            api_data["protocol"] = "HTTPS"
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        api_path = generate_url(
            f"{device_type}/{serial_number}/http", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTPS test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTPS test initiated successfully for {device_type} "
            f"{serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_https_gateways_test(
        central_conn,
        serial_number,
        destination,
        count=None,
        interval=None,
        include_raw_output=None,
    ):
        """Initiates a HTTPS test on the specified Gateway device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination hostname or IP address.
            count (int, optional): Number of ping packets to send (1-10).
            interval (int, optional): Time between ping packets in seconds (1-10).
            include_raw_output (bool, optional): Whether to include raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If count is not a valid integer between 1-10.
            ParameterError: If interval is not a valid integer between 1-10.
            ParameterError: If include_raw_output is not a boolean.
            ParameterError: If destination is not a valid IP address or hostname.
            Exception: If initiating the HTTPS test fails.
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if count and not isinstance(count, int):
            raise ParameterError(
                "Count must be a valid integer from 1-10 and is valid for"
                " device_type=gateways only."
            )
        elif count:
            api_data["count"] = count

        if interval and not isinstance(interval, int):
            raise ParameterError(
                "Interval must be a valid integer from 1-10 and is valid for"
                " device_type=gateways only."
            )
        elif interval:
            api_data["interval"] = interval

        if include_raw_output and not isinstance(include_raw_output, bool):
            raise ParameterError("Include raw output must be a boolean.")
        elif include_raw_output is not None:
            api_data["includeRawOutput"] = bool(include_raw_output)

        if destination and isinstance(destination, str):
            api_data["url"] = destination
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        api_path = generate_url(
            f"{device_type}/{serial_number}/https", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTPS test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTPS test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_https_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """Retrieves the results of a HTTPS test on the specified device.

        Supported device type includes AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If retrieving the test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/https/async-operations/{task_id}",
                "troubleshooting",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get HTTPS test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"HTTPS test for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"HTTPS test for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def iperf_test(
        central_conn,
        device_type,
        serial_number,
        server_address,
        port=None,
        duration=None,
        parallel=None,
        omit=None,
        include_reverse=None,
        vlan_interface=None,
        protocol=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates an iPerf test on the specified device and polls for test result.

        Supported device type includes GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('gateways').
            serial_number (str): Serial number of the device.
            server_address (str): Server address for the iPerf test.
            port (int, optional): TCP port (1-65535).
            duration (int, optional): Transmission time in seconds (10-120).
            parallel (int, optional): Number of parallel streams (1-128).
            omit (int, optional): Omit the first n seconds of the test.
            include_reverse (bool, optional): Include reverse test.
            vlan_interface (str, optional): VLAN interface for the test.
            protocol (str, optional): Protocol to use, 'tcp' or 'udp'.
            include_raw_output (bool, optional): Include raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If initiating the iPerf test fails.
        """

        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("iperf_test"),
        )

        try:
            response = Troubleshooting.initiate_iperf_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                server_address=server_address,
                port=port,
                duration=duration,
                parallel=parallel,
                omit=omit,
                include_reverse=include_reverse,
                vlan_interface=vlan_interface,
                protocol=protocol,
                include_raw_output=include_raw_output,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_iperf_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating iperf test for {device_type} "
                f"{serial_number} on {server_address}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_iperf_test(
        central_conn,
        device_type,
        serial_number,
        server_address,
        port=None,
        duration=None,
        parallel=None,
        omit=None,
        include_reverse=None,
        vlan_interface=None,
        protocol=None,
        include_raw_output=None,
    ):
        """Initiates an iPerf test on the specified device.

        Supported device type includes GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('gateways').
            serial_number (str): Serial number of the device.
            server_address (str): Server address for the iPerf test.
            port (int, optional): TCP port (1-65535).
            duration (int, optional): Transmission time in seconds (10-120).
            parallel (int, optional): Number of parallel streams (1-128).
            omit (int, optional): Omit the first n seconds of the test.
            include_reverse (bool, optional): Include reverse test.
            vlan_interface (str, optional): VLAN interface for the test.
            protocol (str, optional): Protocol to use, 'tcp' or 'udp'.
            include_raw_output (bool, optional): Include raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If server_address is not a valid IP address string.
            ParameterError: If port is not a valid integer between 1-65535.
            ParameterError: If duration is not a valid integer between 10-120.
            ParameterError: If parallel is not a valid integer between 1-128.
            ParameterError: If omit is not a valid integer greater than or equal to 0.
            ParameterError: If include_reverse is not a boolean.
            ParameterError: If vlan_interface is not a valid string.
            ParameterError: If protocol is not 'tcp' or 'udp'.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If initiating the iPerf test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("iperf_test"),
        )

        api_data = dict()

        if not server_address or not isinstance(server_address, str):
            raise ParameterError(
                "Server address must be a valid IP address string."
            )
        elif server_address:
            api_data["iperfServerAddress"] = server_address

        if port and (not isinstance(port, int) or not (1 <= port <= 65535)):
            raise ParameterError(
                "Port must be a valid integer between 1 and 65535."
            )
        elif port:
            api_data["port"] = port

        if duration and (
            not isinstance(duration, int) or not (10 <= duration <= 120)
        ):
            raise ParameterError(
                "Duration must be a valid integer between 10 and 120."
            )
        elif duration:
            api_data["duration"] = duration

        if parallel and (
            not isinstance(parallel, int) or not (1 <= parallel <= 128)
        ):
            raise ParameterError(
                "Parallel must be a valid integer between 1 and 128."
            )
        elif parallel:
            api_data["parallel"] = parallel

        if omit and (not isinstance(omit, int) or omit < 0):
            raise ParameterError(
                "Omit must be a valid integer greater than or equal to 0."
            )
        elif omit:
            api_data["omit"] = omit

        if include_reverse and not isinstance(include_reverse, bool):
            raise ParameterError("Include reverse must be a valid boolean.")
        elif include_reverse is not None:
            api_data["includeReverse"] = include_reverse

        if vlan_interface and not isinstance(vlan_interface, str):
            raise ParameterError("VLAN interface must be a valid string.")
        elif vlan_interface:
            api_data["vlanInterface"] = vlan_interface

        if protocol and protocol.lower() not in ["tcp", "udp"]:
            raise ParameterError("Protocol must be either 'tcp' or 'udp'.")
        elif protocol and protocol.lower() in ["tcp", "udp"]:
            api_data["protocol"] = protocol

        if include_raw_output and not isinstance(include_raw_output, bool):
            raise ParameterError("Include raw output must be a valid boolean.")
        elif include_raw_output is not None:
            api_data["includeRawOutput"] = include_raw_output

        api_path = generate_url(
            f"{device_type}/{serial_number}/iperf", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate iPerf test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"iPerf test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_iperf_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """Retrieves the results of an iPerf test on the specified device.

        Supported device type includes GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If retrieving the test result fails.
        """

        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/iperf/async-operations/{task_id}",
                "troubleshooting",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get iPerf result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"iPerf for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"iPerf for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def locate_device(central_conn, device_type, serial_number):
        """Initiates a locate (e.g., blinking LED) operation on the specified device.

        Supported device type includes AOS-S, AP, and CX.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', or 'cx').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the API.

        Raises:
            Exception: If initiating the locate operation fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("locate_test"),
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/locate", "troubleshooting"
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate locate: {resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Locate initiated successfully for {device_type} {serial_number}. Please check the device for visual confirmation."
        )
        return resp

    @staticmethod
    def nslookup_test(
        central_conn,
        device_type,
        serial_number,
        host,
        dns_server=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates an nslookup test on the specified device and polls for test result.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            host (str): Hostname or domain name for the nslookup test.
            dns_server (str, optional): DNS server address to use.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If initiating the nslookup test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("nslookup_test"),
        )

        try:
            response = Troubleshooting.initiate_nslookup_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                host=host,
                dns_server=dns_server,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_nslookup_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating nslookup test for {device_type} {serial_number} on {host}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_nslookup_test(
        central_conn,
        host,
        device_type,
        serial_number,
        dns_server=None,
    ):
        """Initiates an nslookup test on the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            host (str): Hostname or domain name for the nslookup test.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            dns_server (str, optional): DNS server address to use.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            Exception: If initiating the nslookup test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("nslookup_test"),
        )

        api_data = {"host": host}

        if dns_server is not None:
            api_data["dnsServer"] = dns_server

        api_path = generate_url(
            f"{device_type}/{serial_number}/nslookup", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate Nslookup test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Nslookup test initiated successfully for {device_type} {serial_number} to {host}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_nslookup_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """Retrieves the results of a nslookup test on the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If retrieving the test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/nslookup/async-operations/{task_id}",
                "troubleshooting",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get nslookup test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Nslookup test for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Nslookup test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def ping_aoss_test(
        central_conn,
        serial_number,
        destination,
        use_ipv6=None,
        packet_size=None,
        count=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a ping test on the specified AOS-S device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the ping test.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            packet_size (int, optional): Packet size in bytes (10-2000).
            count (int, optional): Number of ping packets to send.
            source_loopback_port (int, optional): Port to use as source for ping.
            source_vlan (int, optional): VLAN ID to use as source for ping.
            source_ip_address (str, optional): Source IP address to use for ping.
            include_raw_output (str, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error initiating the ping test.

        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_aoss_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                use_ipv6=use_ipv6,
                packet_size=packet_size,
                count=count,
                source_loopback_port=source_loopback_port,
                source_vlan=source_vlan,
                source_ip_address=source_ip_address,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def ping_aps_test(
        central_conn,
        serial_number,
        destination,
        packet_size=None,
        count=None,
        source_interface=None,
        source_vlan=None,
        source_role=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a ping test on the specified AP device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the ping test.
            packet_size (int, optional): Packet size in bytes (10-2000).
            count (int, optional): Number of ping packets to send.
            source_interface (str, optional): Port to use as source for ping.
            source_vlan (int, optional): VLAN ID to use as source for ping.
            source_role (str, optional): Role to use for ping.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error initiating the ping test.
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_aps_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                packet_size=packet_size,
                count=count,
                source_interface=source_interface,
                source_vlan=source_vlan,
                source_role=source_role,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def ping_cx_test(
        central_conn,
        serial_number,
        destination,
        use_ipv6=None,
        packet_size=None,
        count=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a ping test on the specified CX device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the ping test.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            packet_size (int, optional): Packet size in bytes (10-2000).
            count (int, optional): Number of ping packets to send.
            use_management_interface (bool, optional): Boolean indicating whether to
                use management interface.
            vrf_name (str, optional): Name of the VRF to use for the ping test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error initiating the ping test.
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_cx_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                use_ipv6=use_ipv6,
                packet_size=packet_size,
                count=count,
                use_management_interface=use_management_interface,
                vrf_name=vrf_name,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def ping_gateways_test(
        central_conn,
        serial_number,
        destination,
        packet_size=None,
        count=None,
        use_ipv6=None,
        ttl=None,
        dscp=None,
        dont_fragment=None,
        source_interface=None,
        source_vlan=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a ping test on the specified Gateway device and polls for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the ping test.
            packet_size (int, optional): Packet size in bytes (10-2000).
            count (int, optional): Number of ping packets to send.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            ttl (int, optional): Time To Live for IP datagram (1-255).
            dscp (int, optional): DSCP packet header value between 0 and 63(0-63).
            dont_fragment (bool, optional): Boolean indicating whether to fragment or not.
            source_interface (str, optional): Port to use as source for ping.
            source_vlan (int, optional): VLAN ID to use as source for ping.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error initiating the ping test.
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_gateways_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                packet_size=packet_size,
                count=count,
                use_ipv6=use_ipv6,
                ttl=ttl,
                dscp=dscp,
                dont_fragment=dont_fragment,
                source_interface=source_interface,
                source_vlan=source_vlan,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_ping_aoss_test(
        central_conn,
        destination,
        serial_number,
        use_ipv6=None,
        packet_size=None,
        count=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
    ):
        """Initiates a ping test on the specified AOS-S device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the ping test.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            packet_size (int, optional): Size of the ping packets.
            count (int, optional): Number of ping packets to send.
            source_loopback_port (int, optional): Port to use as source for ping.
            source_vlan (int, optional): VLAN ID to use as source for ping.
            source_ip_address (str, optional): Source IP address to use for ping.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If use_ipv6 is not a boolean.
            ParameterError: If packet_size is not an integer.
            ParameterError: If count is not an integer between 1-100.
            ParameterError: If source_loopback_port is not an integer.
            ParameterError: If source_ip_address is not a string.
            ParameterError: If source_vlan is not an integer.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the ping test.
        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if packet_size and isinstance(packet_size, int):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError("packet_size must be an integer value.")

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )

        if source_loopback_port and isinstance(source_loopback_port, int):
            api_data["loopbackPort"] = source_loopback_port
        elif source_loopback_port:
            raise ParameterError(
                "source_loopback_port must be an integer value."
            )
        if source_ip_address and isinstance(source_ip_address, str):
            api_data["ipAddress"] = source_ip_address
        elif source_ip_address:
            raise ParameterError("source_ip_address must be a string value.")

        if source_vlan and isinstance(source_vlan, int):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError("source_vlan must be an integer value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url(
            f"{device_type}/{serial_number}/ping", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_ping_aps_test(
        central_conn,
        destination,
        serial_number,
        packet_size=None,
        count=None,
        source_interface=None,
        source_vlan=None,
        source_role=None,
        include_raw_output=None,
    ):
        """Initiates a ping test on the specified AP device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            destination (str): Destination IP or hostname for the ping test.
            serial_number (str): Serial number of the device.
            packet_size (int, optional): Size of the ping packets.
            count (int, optional): Number of ping packets to send.
            source_interface (str, optional): Port to use as source for ping.
            source_vlan (int, optional): VLAN ID to use as source for ping.
            source_role (str, optional): Role to use for ping.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If packet_size is not an integer between 10-2000.
            ParameterError: If count is not an integer between 1-100.
            ParameterError: If source_interface is not a string.
            ParameterError: If source_vlan is not an integer between 1-4094.
            ParameterError: If source_role is not a string.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the ping test.
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if (
            packet_size
            and isinstance(packet_size, int)
            and 10 <= packet_size <= 2000
        ):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError(
                "packet_size must be an integer value 10-2000."
            )

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )

        if source_interface and isinstance(source_interface, str):
            api_data["interfacePort"] = source_interface
        elif source_interface:
            raise ParameterError("source_interface must be a string value.")

        if (
            source_vlan
            and isinstance(source_vlan, int)
            and 1 <= source_vlan <= 4094
        ):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError(
                "source_vlan must be an integer value 1-4094."
            )

        if source_role and isinstance(source_role, str):
            api_data["role"] = source_role
        elif source_role:
            raise ParameterError("source_role must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url(
            f"{device_type}/{serial_number}/ping", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_ping_cx_test(
        central_conn,
        destination,
        serial_number,
        use_ipv6=None,
        packet_size=None,
        count=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
    ):
        """Initiates a ping test on the specified CX device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            destination (str): Destination IP or hostname for the ping test.
            serial_number (str): Serial number of the device.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            packet_size (int, optional): Size of the ping packets.
            count (int, optional): Number of ping packets to send.
            use_management_interface (bool, optional): Boolean indicating whether to
                use management interface.
            vrf_name (str, optional): Name of the VRF to use for the ping test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If use_ipv6 is not a boolean.
            ParameterError: If packet_size is not an integer.
            ParameterError: If count is not an integer between 1-100.
            ParameterError: If use_management_interface is not a boolean.
            ParameterError: If vrf_name is not a string.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the ping test.
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if packet_size and isinstance(packet_size, int):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError("packet_size must be an integer value.")

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )
        if use_management_interface is not None and isinstance(
            use_management_interface, bool
        ):
            api_data["useManagementInterface"] = use_management_interface
        elif use_management_interface is not None:
            raise ParameterError(
                "use_management_interface must be a boolean value."
            )

        if vrf_name and isinstance(vrf_name, str):
            api_data["vrfName"] = vrf_name
        elif vrf_name:
            raise ParameterError("vrf_name must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url(
            f"{device_type}/{serial_number}/ping", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_ping_gateways_test(
        central_conn,
        destination,
        serial_number,
        packet_size=None,
        count=None,
        use_ipv6=None,
        ttl=None,
        dscp=None,
        dont_fragment=None,
        source_interface=None,
        source_vlan=None,
        include_raw_output=None,
    ):
        """Initiates a ping test on the specified Gateway device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the ping test.
            packet_size (int, optional): Size of the ping packets.
            count (int, optional): Number of ping packets to send.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            ttl (int, optional): Time To Live for IP datagram (1-255).
            dscp (int, optional): DSCP packet header value between 0 and 63(0-63).
            dont_fragment (bool, optional): Boolean indicating whether to fragment or not.
            source_interface (str, optional): Port to use as source for ping.
            source_vlan (int, optional): VLAN ID to use as source for ping.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If packet_size is not an integer between 10-2000.
            ParameterError: If count is not an integer between 1-100.
            ParameterError: If ttl is not an integer between 1-255.
            ParameterError: If dscp is not an integer between 0-63.
            ParameterError: If source_interface is not a string.
            ParameterError: If source_vlan is not an integer between 1-4094.
            ParameterError: If use_ipv6 is not a boolean.
            ParameterError: If dont_fragment is not a boolean.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the ping test.
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if (
            packet_size
            and isinstance(packet_size, int)
            and 10 <= packet_size <= 2000
        ):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError(
                "packet_size must be an integer value 10-2000."
            )

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )

        if ttl and isinstance(ttl, int) and 1 <= ttl <= 255:
            api_data["ttl"] = ttl
        elif ttl:
            raise ParameterError("ttl must be an integer value between 1-255.")

        if dscp and isinstance(dscp, int) and 0 <= dscp <= 63:
            api_data["dscp"] = dscp
        elif dscp:
            raise ParameterError("dscp must be an integer value between 0-63.")

        if source_interface and isinstance(source_interface, str):
            api_data["sourceInterface"] = source_interface
        elif source_interface:
            raise ParameterError("source_interface must be a string value.")

        if (
            source_vlan
            and isinstance(source_vlan, int)
            and 1 <= source_vlan <= 4094
        ):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError(
                "source_vlan must be an integer value 1-4094."
            )

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if dont_fragment and isinstance(dont_fragment, bool):
            api_data["dontFragmentFlag"] = dont_fragment
        elif dont_fragment:
            raise ParameterError("dont_fragment must be a boolean value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url(
            f"{device_type}/{serial_number}/ping", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_ping_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """Retrieves the results of a ping test on the specified device.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If retrieving the ping test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/ping/async-operations/{task_id}",
                "troubleshooting",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get ping test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Ping test for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Ping test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def poe_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a PoE test on the specified device and polls for test results.

        Supported device type includes AOS-S, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            ports (list): List of the ports to test.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error initiating the PoE bounce test.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "poe_bounce_test"
            ),
        )
        try:
            response = Troubleshooting.initiate_poe_bounce_test(
                central_conn=central_conn,
                ports=ports,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_poe_bounce_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating PoE bounce test for {device_type} {serial_number} on {ports}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_poe_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
    ):
        """Initiates a PoE test on the specified device,

        Supported device type includes AOS-S, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            ports (list): List of the ports to test.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If the ports parameter is invalid.
            Exception: If there is an error initiating the PoE bounce test.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "poe_bounce_test"
            ),
        )

        if not ports or not isinstance(ports, list):
            raise ParameterError("Ports must be a non-empty list.")

        api_data = {"ports": ports}

        api_path = generate_url(
            f"{device_type}/{serial_number}/poeBounce", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate PoE test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"PoE bounce test initiated successfully for {device_type} {serial_number} on {ports}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_poe_bounce_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """Retrieves the results of a PoE test on the specified device.

        Supported device type includes AOS-S, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aos-s', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If retrieving the PoE bounce test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "poe_bounce_test"
            ),
        )

        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/poeBounce/async-operations/{task_id}",
                "troubleshooting",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get PoE bounce test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"PoE bounce test for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"PoE bounce test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def port_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a port bounce test on the specified device.

        Supported device type includes AOS-S, CX, and GATEWAY.
        Port bounce test disable/enables port(s).

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            ports (list): List of the ports to test.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error initiating the port bounce test.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "port_bounce_test"
            ),
        )

        try:
            response = Troubleshooting.initiate_port_bounce_test(
                central_conn=central_conn,
                ports=ports,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_port_bounce_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating port bounce test for {device_type} {serial_number} on {ports}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_port_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
    ):
        """Initiates a port bounce test on the specified device.

        Supported device type includes AOS-S, CX, and GATEWAY.
        Port bounce test disable/enables port(s).

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            ports (list): List of the ports to test.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If the ports parameter is invalid.
            Exception: If initiating the port bounce test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "port_bounce_test"
            ),
        )

        if not ports or not isinstance(ports, list):
            raise ParameterError("Ports must be a non-empty list.")

        api_data = {"ports": ports}

        api_path = generate_url(
            f"{device_type}/{serial_number}/portBounce", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate port test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Port bounce test initiated successfully for {device_type} "
            f"{serial_number} on {ports}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_port_bounce_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """Retrieves the results of a port bounce test on the specified device.

        Supported device type includes AOS-S, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aos-s', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If retrieving the port bounce test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "port_bounce_test"
            ),
        )

        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/portBounce/async-operations/{task_id}",
                "troubleshooting",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get port bounce test result: {resp['code']} -"
                f" {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Port bounce test for {device_type} {serial_number} with task"
                f" ID {task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Port bounce test for {device_type} {serial_number} with task"
                f" ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def reboot_device(central_conn, device_type, serial_number):
        """Reboots the specified device.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the API.

        Raises:
            Exception: If initiating the reboot fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/reboot", "troubleshooting"
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate reboot: {resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Reboot initiated successfully for {device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def retrieve_arp_table_test(
        central_conn,
        device_type,
        serial_number,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a ARP table retrieval test on the specified device.

        Supported device type includes AOS-S, AP, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', or 'gateways').
            serial_number (str): Serial number of the device.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error initiating the ARP table retrieval test.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "retrieve_arp_table_test"
            ),
        )
        try:
            response = Troubleshooting.initiate_retrieve_arp_table_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_retrieve_arp_table_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ARP table retrieval test for {device_type}"
                f" {serial_number}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_retrieve_arp_table_test(
        central_conn,
        device_type,
        serial_number,
    ):
        """Initiates a ARP table retrieval test on the specified device.

        Supported device type includes AOS-S, AP, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            Exception: If initiating the ARP table retrieval fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "retrieve_arp_table_test"
            ),
        )

        api_path = generate_url(
            f"{device_type}/{serial_number}/getArpTable", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ARP table retrieval test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"ARP table retrieval test initiated successfully for "
            f"{device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_retrieve_arp_table_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """Retrieves the results of an ARP table retrieval test on the specified
        device.

        Supported device type includes AOS-S, AP, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aos-s', 'aps', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If retrieving the ARP table test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "retrieve_arp_table_test"
            ),
        )

        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/getArpTable/async-operations/{task_id}",
                "troubleshooting",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get ARP table retrieval test result: {resp['code']}"
                f" - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"ARP table retrieval test for {device_type} {serial_number} "
                f"with task ID {task_id} is not yet completed. Current status:"
                f" {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"ARP table retrieval test for {device_type} {serial_number} "
                f"with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def speedtest_test(
        central_conn,
        device_type,
        serial_number,
        iperf_server_address,
        protocol=None,
        server_port=None,
        bandwidth=None,
        include_reverse=None,
        seconds_to_measure=None,
        parallel=None,
        omit=None,
        window_size=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a speed test on the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            iperf_server_address (str): iPerf server address.
            protocol (str, optional): Protocol to use ('tcp' or 'udp').
            server_port (int, optional): Server port (0-65535).
            bandwidth (int, optional): Bandwidth in kbps.
            include_reverse (bool, optional): Include reverse test.
            seconds_to_measure (int, optional): Duration to measure speed in seconds (1-20).
            parallel (int, optional): Number of parallel streams (1-30).
            omit (int, optional): Omit the first n seconds of the test (1-5).
            window_size (int, optional): TCP window size in KB (65-16384).
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test results.

        Raises:
            Exception: If initiating the speedtest test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("speedtest_test"),
        )

        try:
            response = Troubleshooting.initiate_speedtest_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                iperf_server_address=iperf_server_address,
                protocol=protocol,
                server_port=server_port,
                bandwidth=bandwidth,
                include_reverse=include_reverse,
                seconds_to_measure=seconds_to_measure,
                parallel=parallel,
                omit=omit,
                window_size=window_size,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_speedtest_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating speedtest test for {device_type} "
                f"{serial_number} on {iperf_server_address}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_speedtest_test(
        central_conn,
        device_type,
        serial_number,
        iperf_server_address,
        protocol=None,
        server_port=None,
        bandwidth=None,
        include_reverse=None,
        seconds_to_measure=None,
        parallel=None,
        omit=None,
        window_size=None,
    ):
        """Initiates a speed test on the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            iperf_server_address (str): iPerf server address.
            protocol (str, optional): Protocol to use ('tcp' or 'udp').
            server_port (int, optional): Server port (0-65535).
            bandwidth (int, optional): Bandwidth in kbps.
            include_reverse (bool, optional): Include reverse test.
            seconds_to_measure (int, optional): Duration to measure speed in seconds (1-20).
            parallel (int, optional): Number of parallel streams (1-30).
            omit (int, optional): Omit the first n seconds of the test (1-5).
            window_size (int, optional): TCP window size in KB (65-16384).

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If iperf_server_address is not a valid IP address or hostname.
            ParameterError: If protocol is not 'tcp' or 'udp'.
            ParameterError: If server_port is not a valid integer between 0-65535.
            ParameterError: If bandwidth is not a valid integer.
            ParameterError: If include_reverse is not a boolean.
            ParameterError: If seconds_to_measure is not a valid integer between 1-20.
            ParameterError: If parallel is not a valid integer between 1-30.
            ParameterError: If omit is not a valid integer between 1-5.
            ParameterError: If window_size is not a valid integer.
            Exception: If initiating the speedtest fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("speedtest_test"),
        )

        api_data = dict()
        if not iperf_server_address or not isinstance(
            iperf_server_address, str
        ):
            raise ParameterError(
                "Iperf server address must be a valid IP address or hostname."
            )

        api_data["iperfServerAddress"] = iperf_server_address

        if protocol and protocol not in ["tcp", "udp"]:
            raise ParameterError("Protocol must be either tcp or udp.")
        elif protocol:
            api_data["protocol"] = protocol

        if (
            server_port
            and not isinstance(server_port, int)
            or (
                isinstance(server_port, int)
                and not (0 <= server_port <= 65535)
            )
        ):
            raise ParameterError(
                "Server port must be a valid integer between 0 to 65535."
            )
        elif server_port:
            api_data["serverPort"] = server_port

        if bandwidth and not isinstance(bandwidth, int):
            raise ParameterError("Bandwidth must be a valid integer.")
        elif bandwidth:
            api_data["bandwidth"] = bandwidth

        if include_reverse and not isinstance(include_reverse, bool):
            raise ParameterError("Include reverse must be a boolean.")
        elif include_reverse is not None:
            api_data["includeReverse"] = include_reverse

        if (
            seconds_to_measure
            and not isinstance(seconds_to_measure, int)
            or (
                isinstance(seconds_to_measure, int)
                and not 0 < seconds_to_measure <= 20
            )
        ):
            raise ParameterError(
                "Seconds to measure must be a valid integer between 0 to 20."
            )
        elif seconds_to_measure:
            api_data["secondsToMeasure"] = seconds_to_measure

        if (
            parallel
            and not isinstance(parallel, int)
            or (isinstance(parallel, int) and not 0 < parallel <= 30)
        ):
            raise ParameterError(
                "Parallel must be a valid integer between 0 to 30."
            )
        elif parallel:
            api_data["parallel"] = parallel

        if (
            omit
            and not isinstance(omit, int)
            or (isinstance(omit, int) and not 1 <= omit <= 5)
        ):
            raise ParameterError(
                "Omit must be a valid integer between 1 to 5."
            )
        elif omit:
            api_data["omit"] = omit

        if (
            window_size
            and not isinstance(window_size, int)
            or (
                isinstance(window_size, int) and not (64 < window_size <= 1638)
            )
        ):
            raise ParameterError(
                "Window size must be a valid integer between 64 to 1638."
            )
        elif window_size:
            api_data["windowSize"] = window_size

        api_path = generate_url(
            f"{device_type}/{serial_number}/speedtest", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate speedtest: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Speedtest initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_speedtest_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """Retrieves the results of a speed test on the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing test results.

        Raises:
            Exception: If retrieving the speedtest result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/speedtest/async-operations/{task_id}",
                "troubleshooting",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get speedtest result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Speedtest for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Speedtest for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def tcp_test(
        central_conn,
        device_type,
        serial_number,
        host,
        port,
        timeout=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a TCP test on the specified device and polls for test result.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            host (str): Hostname or IP address.
            port (int): TCP port (1-65535).
            timeout (int, optional): Timeout for the test in seconds (1-10).
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If initiating the TCP test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("tcp_test"),
        )

        try:
            response = Troubleshooting.initiate_tcp_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                host=host,
                port=port,
                timeout=timeout,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_tcp_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating tcp test for {device_type} {serial_number}"
                f" on {host}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_tcp_test(
        central_conn,
        device_type,
        serial_number,
        host,
        port,
        timeout=None,
    ):
        """Initiates a TCP test on the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.
            host (str): Hostname or IP address.
            port (int): TCP port (1-65535).
            timeout (int, optional): Timeout for the test in seconds (1-10).

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If host is not a valid IP address or hostname.
            ParameterError: If port is not a valid integer.
            ParameterError: If timeout is not a valid integer.
            Exception: If initiating the TCP test fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("tcp_test"),
        )

        api_data = dict()
        if not host or not isinstance(host, str):
            raise ParameterError(
                "Host must be a valid IP address or hostname."
            )

        api_data["host"] = host

        if port and not isinstance(port, int):
            raise ParameterError("Port must be a valid integer.")
        elif port:
            api_data["port"] = port

        if timeout and not isinstance(timeout, int):
            raise ParameterError("Timeout must be a valid integer.")
        elif timeout:
            api_data["timeout"] = timeout

        api_path = generate_url(
            f"{device_type}/{serial_number}/tcp", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate tcp test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"TCP test initiated successfully for {device_type} "
            f"{serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_tcp_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """Retrieves the results of a TCP test on the specified device.

        Supported device type includes AP.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aps').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing test status and output.

        Raises:
            Exception: If retrieving the TCP test result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/tcp/async-operations/{task_id}",
                "troubleshooting",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get TCP result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"TCP for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"TCP for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def traceroute_aoss_test(
        central_conn,
        serial_number,
        destination,
        source_interface=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a traceroute test on the specified AOS-S device and polls for test
        result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            source_interface (str, optional): Source for traceroute test, options are
                loopback , vlan-interface , or ip-address.
            source_loopback_port (str, optional): Port to use as source for ping,
                source_interface must be set to loopback.
            source_vlan (int, optional): VLAN ID to use as source for ping,
                source_interface must be set to vlan-interface.
            source_ip_address (str, optional): Source IP address to use for ping,
                source_interface must be set to ip-address.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_aoss_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                source_interface=source_interface,
                source_loopback_port=source_loopback_port,
                source_vlan=source_vlan,
                source_ip_address=source_ip_address,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def traceroute_aps_test(
        central_conn,
        serial_number,
        destination,
        source_interface=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a traceroute test on the specified AP device and polls for test
        result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            source_interface (str, optional): Port to use as source for traceroute test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_aps_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                source_interface=source_interface,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def traceroute_cx_test(
        central_conn,
        serial_number,
        destination,
        use_ipv6=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a traceroute test on the specified CX device and polls for test
        result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            use_management_interface (bool, optional): Boolean indicating whether to
                use management interface.
            vrf_name (str, optional): Name of the VRF to use for the traceroute test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_cx_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                use_ipv6=use_ipv6,
                use_management_interface=use_management_interface,
                vrf_name=vrf_name,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def traceroute_gateways_test(
        central_conn,
        serial_number,
        destination,
        source_vlan_ip=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """Initiates a traceroute test on the specified Gateway device and polls
        for test result.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            source_vlan_ip (str, optional): VLAN IP address to use as source for
                traceroute test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_gateways_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                source_vlan_ip=source_vlan_ip,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_traceroute_aoss_test(
        central_conn,
        destination,
        serial_number,
        source_interface=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
    ):
        """Initiates a traceroute test on the specified AOS-S device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            source_interface (str, optional): Source for traceroute test, options are
                loopback , vlan-interface , or ip-address.
            source_loopback_port (int, optional): Port to use as source for ping,
                source_interface must be set to loopback.
            source_vlan (int, optional): VLAN ID to use as source for ping,
                source_interface must be set to vlan-interface.
            source_ip_address (str, optional): Source IP address to use for ping,
                source_interface must be set to ip-address.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If source_interface is not 'loopback', 'vlan-interface', or 'ip-address'.
            ParameterError: If source_loopback_port is not a valid integer.
            ParameterError: If source_vlan is not a valid integer.
            ParameterError: If source_ip_address is not a valid string.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if (
            source_interface
            and isinstance(source_interface, str)
            and source_interface
            in ["loopback", "vlan-interface", "ip-address"]
        ):
            api_data["sourceInterface"] = source_interface
        elif source_interface:
            raise ParameterError(
                "source_interface must be a string value of "
                "loopback, vlan-interface, or ip-address."
            )

        if source_loopback_port and isinstance(source_loopback_port, int):
            api_data["loopbackPort"] = source_loopback_port
        elif source_loopback_port:
            raise ParameterError(
                "source_loopback_port must be an integer value."
            )

        if source_vlan and isinstance(source_vlan, int):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError("source_vlan must be an integer value.")

        if source_ip_address and isinstance(source_ip_address, str):
            api_data["ipAddress"] = source_ip_address
        elif source_ip_address:
            raise ParameterError("source_ip_address must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/traceroute", "troubleshooting"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_traceroute_aps_test(
        central_conn,
        destination,
        serial_number,
        source_interface=None,
        include_raw_output=None,
    ):
        """Initiates a traceroute test on the specified AP device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            source_interface (str, optional): Source interface to use for the
                traceroute test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If source_interface is not a valid string.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if source_interface and isinstance(source_interface, str):
            api_data["sourceInterface"] = source_interface
        elif source_interface:
            raise ParameterError("source_interface must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/traceroute", "troubleshooting"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} "
            f"{serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_traceroute_cx_test(
        central_conn,
        destination,
        serial_number,
        use_ipv6=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
    ):
        """Initiates a traceroute test on the specified CX device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            use_ipv6 (bool, optional): Boolean indicating whether to use IPv6.
            use_management_interface (bool, optional): Boolean indicating whether to use
                management interface.
            vrf_name (str, optional): Name of the VRF to use for the traceroute test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If use_ipv6 is not a boolean.
            ParameterError: If use_management_interface is not a boolean.
            ParameterError: If vrf_name is not a valid string.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "cx"
        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if use_management_interface is not None and isinstance(
            use_management_interface, bool
        ):
            api_data["useManagementInterface"] = use_management_interface
        elif use_management_interface is not None:
            raise ParameterError(
                "use_management_interface must be a boolean value."
            )

        if vrf_name and isinstance(vrf_name, str):
            api_data["vrfName"] = vrf_name
        elif vrf_name:
            raise ParameterError("vrf_name must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/traceroute", "troubleshooting"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} "
            f"{serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_traceroute_gateways_test(
        central_conn,
        destination,
        serial_number,
        source_vlan_ip=None,
        include_raw_output=None,
    ):
        """Initiates a traceroute test on the specified Gateway device.

        Args:
            central_conn (NewCentralBase): Central connection object.
            serial_number (str): Serial number of the device.
            destination (str): Destination IP or hostname for the traceroute test.
            source_vlan_ip (str, optional): VLAN IP address to use as source for
                traceroute test.
            include_raw_output (bool, optional): Boolean indicating whether to include
                raw output in the response.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If destination is not a valid IP address or hostname.
            ParameterError: If source_vlan_ip is not a valid string.
            ParameterError: If include_raw_output is not a boolean.
            Exception: If there is an error initiating the traceroute test.
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if source_vlan_ip and isinstance(source_vlan_ip, str):
            api_data["vlanIp"] = source_vlan_ip
        elif source_vlan_ip:
            raise ParameterError("source_vlan_ip must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url(
                f"{device_type}/{serial_number}/traceroute", "troubleshooting"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_traceroute_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """Retrieves the result of a traceroute test on the specified device.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API.

        Raises:
            Exception: If there is an error retrieving the traceroute test result.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/traceroute/async-operations/{task_id}",
                "troubleshooting",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get traceroute test result: {resp['code']} -"
                f" {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Traceroute test for {device_type} {serial_number} with "
                f"task ID {task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Traceroute test for {device_type} {serial_number} with task "
                f"ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def list_active_tasks(central_conn, device_type, serial_number):
        """Retrieves a list of all active or recently completed asynchronous operations for the specified device, grouped by test name.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.
        Results are sorted by startTime in descending order (most recently started first).

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response dictionary containing code (int), msg (list of task groups),
                and other metadata. Each task group contains testName (str) and locations (list).
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=["aps", "gateways", "cx", "aos-s"],
        )

        api_path = generate_url(
            f"{device_type}/{serial_number}/list-tasks", "troubleshooting"
        )
        resp = central_conn.command(api_method="GET", api_path=api_path)

        if resp["code"] != 200:
            raise Exception(
                f"Failed to list active tasks for {device_type} {serial_number}: {resp['code']} - {resp['msg']}"
            )

        return resp

    @staticmethod
    def list_show_commands(central_conn, device_type, serial_number):
        """Returns most used/top 'show' commands supported on given device.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (list or dict): List of show commands organized by category if successful (code 200),
                otherwise full response dict containing error information.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=["aps", "gateways", "cx", "aos-s"],
        )

        api_path = generate_url(
            f"{device_type}/{serial_number}/show-commands", "troubleshooting"
        )
        resp = central_conn.command(api_method="GET", api_path=api_path)

        if resp["code"] != 200:
            raise Exception(
                f"Failed to list show commands for {device_type} {serial_number}: {resp['code']} - {resp['msg']}"
            )

        return resp["msg"]

    @staticmethod
    def run_show_commands(
        central_conn,
        device_type,
        serial_number,
        commands,
        max_attempts=5,
        poll_interval=5,
    ):
        """Runs 'show' command(s) on a device and polls for test result.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.
        All commands must start with 'show '.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            commands (str or list): Single show command as string (e.g., "show version") or
                list of show commands (e.g., ["show version", "show ip route"]). Max 20 commands.
                All commands must start with 'show '.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.

        Returns:
            (dict): Response from the test results API containing command output and status.

        Raises:
            Exception: If initiating the show command fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=["aps", "gateways", "cx", "aos-s"],
        )

        try:
            response = Troubleshooting.initiate_show_commands(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                commands=commands,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_show_commands_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error running show command on {device_type} {serial_number}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_show_commands(
        central_conn, device_type, serial_number, commands
    ):
        """Initiates an asynchronous execution of 'show' command(s) on a device.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.
        All commands must start with 'show '.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            commands (str or list): Single show command as string (e.g., "show version") or
                list of show commands (e.g., ["show version", "show ip route"]). Max 20 commands.
                All commands must start with 'show '.

        Returns:
            (dict): Response from the API containing task ID and other details.

        Raises:
            ParameterError: If commands is not a valid string or list.
            ParameterError: If commands list is empty or exceeds 20 items.
            ParameterError: If any command doesn't start with 'show '.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=["aps", "gateways", "cx", "aos-s"],
        )

        # Normalize commands to a list
        if isinstance(commands, str):
            # Single command provided as string
            if not commands or not commands.strip():
                raise ParameterError("commands must be a non-empty string")

            if not commands.strip().lower().startswith("show "):
                raise ParameterError(
                    "Command must start with 'show '. Example: 'show ap debug system-status'"
                )

            commands_list = [commands]

        elif isinstance(commands, list):
            # List of commands provided
            if len(commands) == 0:
                raise ParameterError("commands list cannot be empty")

            if len(commands) > 20:
                raise ParameterError(
                    f"commands list cannot exceed 20 items. Provided: {len(commands)}"
                )

            # Validate each command in the list
            for idx, cmd in enumerate(commands):
                if not cmd or not isinstance(cmd, str) or not cmd.strip():
                    raise ParameterError(
                        f"Command at index {idx} must be a valid non-empty string"
                    )

                if not cmd.strip().lower().startswith("show "):
                    raise ParameterError(
                        f"Command at index {idx} must start with 'show '. Got: '{cmd}'"
                    )

            commands_list = commands

        else:
            raise ParameterError(
                "commands must be either a string (single command) or a list of strings (multiple commands)"
            )

        api_data = {"commands": commands_list}

        api_path = generate_url(
            f"{device_type}/{serial_number}/showCommands", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate show command for {device_type} {serial_number}: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Show command initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_show_commands_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """Retrieves the results of a show command execution on a device with the provided task ID.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            task_id (str): Task ID to poll for.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.

        Returns:
            (dict): Response from the test results API containing command output and status.

        Raises:
            Exception: If retrieving the command result fails.
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=["aps", "gateways", "cx", "aos-s"],
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url(
                f"{device_type}/{serial_number}/showCommands/async-operations/{task_id}",
                "troubleshooting",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get show command result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Show command for {device_type} {serial_number} with task ID {task_id} "
                f"is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Show command for {device_type} {serial_number} with task ID {task_id} "
                f"has successfully completed."
            )

        return resp["msg"]

    @staticmethod
    def list_events(
        central_conn,
        context_type,
        context_id,
        site_id,
        start_at=None,
        end_at=None,
        duration=None,
        search=None,
        filter_str=None,
        sort=None,
        next_cursor=1,
        limit=100,
    ):
        """Retrieves a list of Network Events based on the query parameters provided.

        Each Event in the returned list includes details like event name, category,
        source type, severity, etc. The query parameters allow you to narrow down
        the results that meet specific criteria.

        Args:
            central_conn (NewCentralBase): Central connection object.
            context_type (str): Type of context ('SITE', 'ACCESS_POINT', 'SWITCH',
                'GATEWAY', 'WIRELESS_CLIENT', 'WIRED_CLIENT', or 'BRIDGE').
            context_id (str): Context Id (site id, device serial number or client
                mac address). Max length 128.
            site_id (str): Site ID to filter the event details for a specific site.
                Max length 128.
            start_at (str, optional): Data is required starting from this timestamp,
                provided in RFC 3339 (and ISO 8601) format in the UTC+0 timezone.
                Must be provided together with end_at when duration is not used.
                The difference between end_at and start_at must not exceed 30 days.
            end_at (str, optional): Data is required up to this timestamp, provided
                in RFC 3339 (and ISO 8601) format in the UTC+0 timezone. Must be
                provided together with start_at when duration is not used.
            duration (str, optional): Relative event window such as '3h', '2d',
                '1w', or '30m'. Provide either duration or both start_at and end_at,
                but not both. Maximum supported duration is 30 days.
            search (str, optional): Search events by name, serial number, host name,
                client mac address or device mac address. Full text search is not
                supported. Search is restricted to meta-data. Max length 256.
            filter_str (str, optional): OData Version 4.0 filter string (limited
                functionality). Supports only 'and' conjunction ('or' and 'not' are
                NOT supported). Supported fields: eventId, category, sourceType with
                operators 'eq' and 'in'. Max length 512.
            sort (str, optional): Sort expressions. Sort expression is a property
                name optionally followed by a direction indicator 'asc' (ascending)
                or 'desc' (descending). If direction is omitted, default is descending.
                Supported field: timestamp. Max length 128.
            next_cursor (int or str, optional): Specifies the pagination cursor for the next
                page of resources. Minimum value is 1. Defaults to 1.
            limit (int, optional): Maximum number of events to be retrieved. Allowed
                range is 1 to 1000. Defaults to 100.

        Returns:
            (dict): Response containing:
                - events (list): List of event dictionaries with fields like eventId,
                    uuid, serialNumber, timestamp, eventName, category, sourceType,
                    sourceName, description, severity, etc.
                - count (int): Number of events in current response.
                - total (int): Total number of events matching the criteria.
                - next (int): Pagination cursor for the next page.

        Raises:
            ParameterError: If context_type is not a valid value.
            ParameterError: If context_id exceeds 128 characters.
            ParameterError: If the time window parameters are invalid.
            ParameterError: If site_id exceeds 128 characters.
            ParameterError: If search exceeds 256 characters.
            ParameterError: If filter_str exceeds 512 characters.
            ParameterError: If sort exceeds 128 characters.
            ParameterError: If next_cursor is not an integer/string >= 1.
            ParameterError: If limit is not between 1 and 1000.
            Exception: If retrieving the events fails.
        """
        valid_context_types = [
            "SITE",
            "ACCESS_POINT",
            "SWITCH",
            "GATEWAY",
            "WIRELESS_CLIENT",
            "WIRED_CLIENT",
            "BRIDGE",
        ]

        # Validate required parameters
        if not context_type or context_type not in valid_context_types:
            raise ParameterError(
                f"context_type must be one of {', '.join(valid_context_types)}"
            )

        if not context_id or not isinstance(context_id, str):
            raise ParameterError("context_id must be a non-empty string")
        elif len(context_id) > 128:
            raise ParameterError("context_id must not exceed 128 characters")

        if not site_id or not isinstance(site_id, str):
            raise ParameterError("site_id must be a non-empty string")
        elif len(site_id) > 128:
            raise ParameterError("site_id must not exceed 128 characters")

        try:
            start_at, end_at = build_timestamp_filter(
                start_time=start_at,
                end_time=end_at,
                duration=duration,
                fmt="rfc3339",
                max_period_days=30,
            )
        except ValueError as e:
            raise ParameterError(str(e)) from e

        # Validate optional parameters
        if search is not None:
            if not isinstance(search, str):
                raise ParameterError("search must be a string")
            elif len(search) > 256:
                raise ParameterError("search must not exceed 256 characters")

        if filter_str is not None:
            if not isinstance(filter_str, str):
                raise ParameterError("filter_str must be a string")
            elif len(filter_str) > 512:
                raise ParameterError(
                    "filter_str must not exceed 512 characters"
                )

        if sort is not None:
            if not isinstance(sort, str):
                raise ParameterError("sort must be a string")
            elif len(sort) > 128:
                raise ParameterError("sort must not exceed 128 characters")

        if not isinstance(next_cursor, (int, str)):
            raise ParameterError("next_cursor must be an integer or string")
        if isinstance(next_cursor, int) and next_cursor < 1:
            raise ParameterError("next_cursor must be >= 1")
        if isinstance(next_cursor, str):
            try:
                if int(next_cursor) < 1:
                    raise ParameterError("next_cursor must be >= 1")
            except ValueError:
                raise ParameterError("next_cursor must be a numeric string")

        if not isinstance(limit, int) or not (1 <= limit <= 1000):
            raise ParameterError("limit must be an integer between 1 and 1000")

        # Build query parameters
        params = {
            "context-type": context_type,
            "context-identifier": context_id,
            "start-at": start_at,
            "end-at": end_at,
            "site-id": site_id,
            "next": next_cursor,
            "limit": limit,
        }

        if search is not None:
            params["search"] = search

        if filter_str is not None:
            params["filter"] = filter_str

        if sort is not None:
            params["sort"] = sort

        api_path = generate_url("events", "troubleshooting")
        resp = central_conn.command(
            api_method="GET", api_path=api_path, api_params=params
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to list events: {resp['code']} - {resp['msg']}"
            )

        central_conn.logger.info(
            f"Successfully retrieved {resp['msg'].get('count', 0)} events "
            f"for context {context_type} {context_id}"
        )

        return resp["msg"]

    @staticmethod
    def list_event_filters(
        central_conn,
        context_type,
        context_id,
        site_id,
        start_at=None,
        end_at=None,
        duration=None,
    ):
        """Retrieves available filter options for network events.

        Returns categories, source types, and event names with their
        respective counts. Use this information to construct filters for
        the list_events API.

        Args:
            central_conn (NewCentralBase): Central connection object.
            context_type (str): Type of context ('SITE', 'ACCESS_POINT', 'SWITCH',
                'GATEWAY', 'WIRELESS_CLIENT', 'WIRED_CLIENT', or 'BRIDGE').
            context_id (str): Context identifier (site ID, device serial number
                or client MAC address). Max length 128.
            site_id (str): Site ID to filter the event details for a specific site.
                Max length 128.
            start_at (str, optional): Data is required starting from this timestamp,
                provided in RFC 3339 (and ISO 8601) format in the UTC+0 timezone.
                Must be provided together with end_at when duration is not used.
                The difference between end_at and start_at must not exceed 30 days.
            end_at (str, optional): Data is required up to this timestamp, provided
                in RFC 3339 (and ISO 8601) format in the UTC+0 timezone. Must be
                provided together with start_at when duration is not used.
            duration (str, optional): Relative event window such as '3h', '2d',
                '1w', or '30m'. Provide either duration or both start_at and end_at,
                but not both. Maximum supported duration is 30 days.


        Returns:
            (dict): Response containing available filter options including
                categories, source types, and event names with counts.

        Raises:
            ParameterError: If context_type is not a valid value.
            ParameterError: If context_id exceeds 128 characters.
            ParameterError: If the time window parameters are invalid.
            ParameterError: If site_id exceeds 128 characters.
            Exception: If retrieving the event filters fails.
        """
        valid_context_types = [
            "SITE",
            "ACCESS_POINT",
            "SWITCH",
            "GATEWAY",
            "WIRELESS_CLIENT",
            "WIRED_CLIENT",
            "BRIDGE",
        ]

        if not context_type or context_type not in valid_context_types:
            raise ParameterError(
                f"context_type must be one of {', '.join(valid_context_types)}"
            )

        if not context_id or not isinstance(context_id, str):
            raise ParameterError("context_id must be a non-empty string")
        elif len(context_id) > 128:
            raise ParameterError("context_id must not exceed 128 characters")

        if not site_id or not isinstance(site_id, str):
            raise ParameterError("site_id must be a non-empty string")
        elif len(site_id) > 128:
            raise ParameterError("site_id must not exceed 128 characters")

        try:
            start_at, end_at = build_timestamp_filter(
                start_time=start_at,
                end_time=end_at,
                duration=duration,
                fmt="rfc3339",
                max_period_days=30,
            )
        except ValueError as e:
            raise ParameterError(str(e)) from e

        params = {
            "context-type": context_type,
            "context-identifier": context_id,
            "start-at": start_at,
            "end-at": end_at,
            "site-id": site_id,
        }

        api_path = generate_url("event-filters", "troubleshooting")
        resp = central_conn.command(
            api_method="GET", api_path=api_path, api_params=params
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to list event filters: {resp['code']} - {resp['msg']}"
            )

        central_conn.logger.info(
            f"Successfully retrieved event filters for context "
            f"{context_type} {context_id}"
        )

        return resp["msg"]

    @staticmethod
    def get_event_extra_attributes(
        central_conn,
        event_identifier,
        site_id,
        time_at,
    ):
        """Retrieves extra attributes of an event.

        The response includes event attributes as key-value pairs providing
        additional detail beyond what is returned in the list_events response.

        Args:
            central_conn (NewCentralBase): Central connection object.
            event_identifier (str): Unique identifier of the event to retrieve
                details for. Max length 128.
            site_id (str): Site ID to filter the event details for a specific site.
                Max length 128.
            time_at (str): Timestamp of when the event occurred, provided in
                RFC 3339 (and ISO 8601) format in the UTC+0 timezone with
                milliseconds. Max length 30.

        Returns:
            (dict): Response containing event extra attributes as key-value pairs.

        Raises:
            ParameterError: If event_identifier exceeds 128 characters.
            ParameterError: If site_id exceeds 128 characters.
            ParameterError: If time_at is not a valid string.
            Exception: If retrieving the event extra attributes fails.
        """
        if not event_identifier or not isinstance(event_identifier, str):
            raise ParameterError(
                "event_identifier must be a non-empty string"
            )
        elif len(event_identifier) > 128:
            raise ParameterError(
                "event_identifier must not exceed 128 characters"
            )

        if not site_id or not isinstance(site_id, str):
            raise ParameterError("site_id must be a non-empty string")
        elif len(site_id) > 128:
            raise ParameterError("site_id must not exceed 128 characters")

        if not time_at or not isinstance(time_at, str):
            raise ParameterError(
                "time_at must be a valid RFC 3339 timestamp string"
            )

        params = {
            "event-identifier": event_identifier,
            "site-id": site_id,
            "time-at": time_at,
        }

        api_path = generate_url(
            "event-extra-attributes", "troubleshooting"
        )
        resp = central_conn.command(
            api_method="GET", api_path=api_path, api_params=params
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get event extra attributes: {resp['code']} "
                f"- {resp['msg']}"
            )

        central_conn.logger.info(
            f"Successfully retrieved extra attributes for event "
            f"{event_identifier}"
        )

        return resp["msg"]

    @staticmethod
    def _poll_task_completion(
        get_result_func,
        task_id,
        conn,
        max_attempts=5,
        poll_interval=5,
        *args,
        **kwargs,
    ):
        """Generic polling method for task completion with configurable timeout.

        Args:
            get_result_func (callable): Function to call for getting task result.
            task_id (str): Task ID to poll for.
            conn (NewCentralBase): Central connection object.
            max_attempts (int, optional): Maximum number of polling attempts.
            poll_interval (int, optional): Time to wait between polls in seconds.
            args: Additional positional arguments for get_result_func.
            kwargs: Additional keyword arguments for get_result_func.

        Returns:
            (dict): Final result from get_result_func.
        """
        for attempt in range(max_attempts):
            result = get_result_func(conn, task_id, *args, **kwargs)
            if result["status"] in ["COMPLETED", "FAILED"]:
                return result
            time.sleep(poll_interval)

        conn.logger.warning(
            f"Task {task_id} did not complete after {max_attempts} attempts. "
            f"Current status: {result['status']}"
        )
        return result

    @staticmethod
    def _get_task_id(api_response):
        """Extracts the task ID from the API response.

        Args:
        api_response (dict): The API response containing the task information.

        Returns:
            (str): The extracted task ID.
        """
        return api_response.get("location", "").split("/")[-1]

    @staticmethod
    def _validate_required_device_params(
        central_conn, device_type, serial_number, subset=None
    ):
        """Validates required parameters are set.

        Supported device type includes AOS-S, AP, CX, and GATEWAY.

        Args:
            central_conn (NewCentralBase): Central connection object.
            device_type (str): Type of the device ('aos-s', 'aps', 'cx', or 'gateways').
            serial_number (str): Serial number of the device.
            subset (list, optional): Subset of supported device types.

        Returns:
            (str): Verified device_type in lower case format.

        Raises:
            ParameterError: If any required parameter is missing.
            ParameterError: If device type is unsupported.
        """
        if not central_conn or not device_type or not serial_number:
            raise ParameterError(
                "central_conn(Central connection), device_type(aps, cx, aos-s,"
                " gateways) and serial_number are required"
            )
        if (subset and device_type.lower() not in subset) or (
            device_type.lower() not in SUPPORTED_DEVICE_TYPES
        ):
            supported_devices = ", ".join(
                subset if subset else SUPPORTED_DEVICE_TYPES
            )
            raise ParameterError(
                f"Unsupported device type: {device_type}, supported types are "
                f"{supported_devices}"
            )
        return device_type.lower()
