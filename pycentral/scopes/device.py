# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.new_monitoring.devices import MonitoringDevices
from .scope_base import ScopeBase
from .scope_maps import ScopeMaps
from ..utils.scope_utils import fetch_attribute
from ..utils.constants import SUPPORTED_CONFIG_PERSONAS
from ..utils.troubleshooting_utils import TROUBLESHOOTING_METHOD_DEVICE_MAPPING
from ..troubleshooting import Troubleshooting

scope_maps = ScopeMaps()

CX_API_ENDPOINT = "cx"
AOS_S_API_ENDPOINT = "aos-s"

# Device type mapping from Central API device types to troubleshooting API endpoints
DEVICE_TYPE_MAPPING = {
    "ACCESS_POINT": "aps",
    "GATEWAY": "gateways",
    "SWITCH": None,  # Requires OS identification for switches
}

# Switch OS mapping based on model prefixes
SWITCH_OS_MAPPING = {
    # AOS-CX prefixes
    "6": CX_API_ENDPOINT,  # 6xxx series
    "8": CX_API_ENDPOINT,  # 8xxx series
    "9": CX_API_ENDPOINT,  # 9xxx series
    "1": CX_API_ENDPOINT,  # 10xx series
    "4": CX_API_ENDPOINT,  # 4xxx series
    # AOS-Switch (AOS-S) prefixes
    "2": AOS_S_API_ENDPOINT,  # 2xxx series
    "3": AOS_S_API_ENDPOINT,  # 3xxx series
    "5": AOS_S_API_ENDPOINT,  # 5xxx series
}

API_ATTRIBUTE_MAPPING = {
    "scopeId": "id",
    "deviceName": "name",
    "deviceGroupName": "group_name",
    "deviceGroupId": "group_id",
    "serialNumber": "serial",
    "deployment": "deployment",
    "siteName": "site_name",
    "siteId": "site_id",
    "macAddress": "mac",
    "model": "model",
    "persona": "persona",
    "firmwareVersion": "firmware-version",
    "role": "role",
    "partNumber": "part-number",
    "isProvisioned": "provisioned_status",
    "status": "status",
    "deviceType": "device_type",
    "ipv4": "ipv4",
    "deviceFunction": "device_function",
}

REQUIRED_ATTRIBUTES = ["name", "serial"]


class Device(ScopeBase):
    """This class holds device and all of its attributes & related methods."""

    def __init__(
        self,
        device_attributes=None,
        central_conn=None,
        serial=None,
        from_api=False,
    ):
        """Constructor for Device object.

        Args:
            device_attributes (dict, optional): Attributes of the Device
            central_conn (NewCentralBase, optional): Instance of NewCentralBase
                to establish connection to Central
            serial (str, optional): Serial number of the device (required if device_attributes
                is not provided)
            from_api (bool, optional): Boolean indicates if the device_attributes is from the
                Central API response

        Raises:
            ValueError: If neither serial nor device_attributes is provided
        """

        # If device_attributes is provided, use it to set attributes
        self.materialized = False
        self.central_conn = central_conn
        self.type = "device"
        if from_api:
            if device_attributes is None:
                raise ValueError(
                    "'device_attributes' must be provided when 'from_api=True'."
                )
            self._apply_api_attributes(device_attributes)
            self.materialized = True
        # If only serial is provided, set it and defer fetching other details
        elif serial:
            self.serial = serial

        # If neither serial nor device_attributes is provided, raise an error
        else:
            raise ValueError(
                "Either 'serial' or 'device_attributes(from api response)' must be provided to create a Device."
            )

    def get_serial(self):
        """Returns the serial number of the device.

        Returns:
            (str): Value of self.serial
        """
        return fetch_attribute(self, "serial")

    def get(self):
        """Fetches the device details from the Central API using the serial number.

        Returns:
            (dict): Device attributes as a dictionary

        Raises:
            Exception: If central_conn is not set
        """
        if self.central_conn is None:
            raise Exception(
                "Unable to get device without Central connection. Please provide the central connection with the central_conn variable."
            )

        device_data = MonitoringDevices.get_device_inventory(
            central_conn=self.central_conn,
            filter_str=f"serialNumber eq {self.get_serial()}",
            limit=1,
        )
        self.materialized = len(device_data["items"]) == 1
        if not self.materialized:
            self.central_conn.logger.error(
                f"Unable to fetch device {self.get_serial()} from Central"
            )
        else:
            self._apply_api_attributes(device_data["items"][0])
            self.central_conn.logger.info(
                f"Successfully fetched device {self.get_serial()}'s data from Central."
            )
        return device_data

    @staticmethod
    def get_all_devices(central_conn, new_central_provisioned=False):
        """Fetches all devices from Central, optionally filtering for new Central configured devices.

        Args:
            central_conn (NewCentralBase): Instance of NewCentralBase to establish connection to Central
            new_central_provisioned (bool, optional): If True, only devices that are provisioned
                via New Central are returned

        Returns:
            (list): List of device dictionaries fetched from Central
        """
        device_list = MonitoringDevices.get_all_device_inventory(
            central_conn=central_conn
        )

        if device_list is None:
            central_conn.logger.error(
                "Failed to fetch device inventory from Central API."
            )
            return []

        if new_central_provisioned:
            return [
                device
                for device in device_list
                if device.get("isProvisioned") == "Yes"
            ]
        return device_list

    def _apply_api_attributes(self, raw_api_dict):
        """Renames API response keys and applies them as object attributes.

        Also sets assigned_profiles to an empty list and assigns config_persona
        if the device is provisioned and its device_function is a supported persona.

        Args:
            raw_api_dict (dict): Raw dict from the Central API response
        """
        device_attributes = self.__rename_keys(raw_api_dict, API_ATTRIBUTE_MAPPING)
        device_attributes["assigned_profiles"] = []
        for key, value in device_attributes.items():
            setattr(self, key, value)

        device_function = device_attributes.get("device_function")
        if (
            getattr(self, "provisioned_status", False)
            and device_function in SUPPORTED_CONFIG_PERSONAS
        ):
            self.config_persona = SUPPORTED_CONFIG_PERSONAS[device_function]
        elif device_function not in SUPPORTED_CONFIG_PERSONAS and device_function != '-':
            self.central_conn.logger.warning(
                f"Device function '{device_function}' is not a supported "
                f"persona. 'config_persona' will not be set for device "
                f"{self.get_serial()}."
            )

    def __rename_keys(self, api_dict, api_attribute_mapping):
        """Renames the keys of the attributes from the API response.

        Args:
            api_dict (dict): Dict from Central API Response
            api_attribute_mapping (dict): Dict mapping API keys to object attributes

        Returns:
            (dict): Renamed dictionary of object attributes
        """
        integer_attributes = {"scopeId"}
        renamed_dict = {}
        for key, value in api_dict.items():
            new_key = api_attribute_mapping.get(key)
            if not new_key:
                continue  # Skip unknown keys
            if key in integer_attributes and value is not None:
                value = int(value)
            if key == "isProvisioned":
                value = True if value == "Yes" else False
            renamed_dict[new_key] = value
        return renamed_dict

    def ping_test(self, destination, **kwargs):
        """Initiates a ping test to the specified destination from the device.

        Args:
            destination (str): The IP address or hostname to ping
            **kwargs (dict, Optional): Optional arguments specific to device type. See below for details:

                - CX switches - [Troubleshooting.ping_cx_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.ping_cx_test) parameters.
                - AOS-S switches - [Troubleshooting.ping_aoss_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.ping_aoss_test) parameters.
                - Access Points - [Troubleshooting.ping_aps_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.ping_aps_test) parameters.
                - Gateways - [Troubleshooting.ping_gateways_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.ping_gateways_test) parameters.
        Returns:
            (dict): Result of the ping test

        Raises:
            ValueError: If device type is unsupported
        """
        if (
            self.device_type == "SWITCH"
            and self._identify_switch_os() == CX_API_ENDPOINT
        ):
            return Troubleshooting.ping_cx_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif (
            self.device_type == "SWITCH"
            and self._identify_switch_os() == AOS_S_API_ENDPOINT
        ):
            return Troubleshooting.ping_aoss_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "ACCESS_POINT":
            return Troubleshooting.ping_aps_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "GATEWAY":
            return Troubleshooting.ping_gateways_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        else:
            raise ValueError(
                f"Ping test is not supported for device type {self.device_type}."
            )

    def traceroute_test(self, destination, **kwargs):
        """Initiates a traceroute test to the specified destination from the device.

        Supported device types: All (aps, cx, aos-s, gateways)

        Args:
            destination (str): The IP address or hostname to traceroute
            **kwargs (dict, Optional): Optional arguments specific to device type. See below for details:

                - CX switches - [Troubleshooting.traceroute_cx_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.traceroute_cx_test) parameters.
                - AOS-S switches - [Troubleshooting.traceroute_aoss_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.traceroute_aoss_test) parameters.
                - Access Points - [Troubleshooting.traceroute_aps_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.traceroute_aps_test) parameters.
                - Gateways - [Troubleshooting.traceroute_gateways_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.traceroute_gateways_test) parameters.
        Returns:
            (dict): Result of the traceroute test

        Raises:
            ValueError: If device type is unsupported
        """
        if (
            self.device_type == "SWITCH"
            and self._identify_switch_os() == CX_API_ENDPOINT
        ):
            return Troubleshooting.traceroute_cx_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif (
            self.device_type == "SWITCH"
            and self._identify_switch_os() == AOS_S_API_ENDPOINT
        ):
            return Troubleshooting.traceroute_aoss_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "ACCESS_POINT":
            return Troubleshooting.traceroute_aps_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "GATEWAY":
            return Troubleshooting.traceroute_gateways_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        else:
            raise ValueError(
                f"traceroute test is not supported for device type {self.device_type}."
            )

    def reboot(self):
        """Reboots the device.

        Supported device types: All (aps, cx, aos-s, gateways)

        Returns:
            (dict): Result of the reboot operation
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.reboot_device
        )

    def locate_test(self):
        """Initiates a locate test (LED blinking) on the device.

        Supported device types: cx, aps, aos-s (gateways not supported)

        Returns:
            (dict): Result of the locate test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.locate_device
        )

    def disconnect_all_clients(self):
        """Disconnects all clients from the specified device.

        Supported device types: gateways (other devices not supported)

        Returns:
            (dict): Result of the disconnect all clients operation
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.disconnect_all_clients
        )

    def disconnect_all_users(self):
        """Disconnects all users from the specified device.

        Supported device types: aps (other devices not supported)

        Returns:
            (dict): Result of the disconnect all users operation
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.disconnect_all_users
        )

    def disconnect_client_mac_addr(self, mac_address):
        """Disconnects client with the specified MAC address on the device.

        Supported device types: gateways (other devices not supported)

        Args:
            mac_address (str): The MAC address from which to disconnect client

        Returns:
            (dict): Result of the disconnect client operation
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.disconnect_client_mac_addr,
            mac_address=mac_address,
        )

    def disconnect_user_mac_addr(self, mac_address):
        """Disconnects user with the specified MAC address on the device.

        Supported device types: aps (other devices not supported)

        Args:
            mac_address (str): The MAC address from which to disconnect user

        Returns:
            (dict): Result of the disconnect user operation
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.disconnect_user_mac_addr,
            mac_address=mac_address,
        )

    def disconnect_all_users_ssid(self, network):
        """Disconnects all users from the specified SSID on the device.

        Supported device types: aps (other devices not supported)

        Args:
            network (str): The SSID from which to disconnect users

        Returns:
            (dict): Result of the disconnect all users operation
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.disconnect_all_users_ssid, network=network
        )

    def http_test(self, destination, **kwargs):
        """Initiates an HTTP test to the specified destination from the device.

        Supported device types: cx, aps, gateways

        Args:
            destination (str): The IP address or hostname to test
            **kwargs (dict, Optional): Optional arguments specific to device
                type, see [Troubleshooting.http_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.http_test)
                for detailed parameter information.

        Returns:
            (dict): Result of the HTTP test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.http_test, destination=destination, **kwargs
        )

    def https_test(self, destination, **kwargs):
        """Initiates an HTTPS test to the specified destination from the device.

        Supported device types: aps, gateways, cx (uses HTTP endpoint with HTTPS protocol)

        Args:
            destination (str): The IP address or hostname to test
            **kwargs (dict, Optional): Optional arguments specific to device type. See below for details:

                - CX switches - [Troubleshooting.https_cx_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.https_cx_test) parameters.
                - Access Points - [Troubleshooting.https_aps_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.https_aps_test) parameters.
                - Gateways - [Troubleshooting.https_gateways_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.https_gateways_test) parameters.

        Returns:
            (dict): Result of the HTTPS test

        Raises:
            ValueError: If device type is unsupported
        """
        self._ensure_materialized()

        if (
            self.device_type == "SWITCH"
            and self._identify_switch_os() == CX_API_ENDPOINT
        ):
            return Troubleshooting.https_cx_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "ACCESS_POINT":
            return Troubleshooting.https_aps_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "GATEWAY":
            return Troubleshooting.https_gateways_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        else:
            raise ValueError(
                f"HTTPS test is not supported for device type {self.device_type}."
            )

    def port_bounce_test(self, ports, **kwargs):
        """Initiates a port bounce test on the specified ports.

        Supported device types: cx, aos-s, gateways

        Args:
            ports (list): List of ports to test
            **kwargs (dict, Optional): Optional arguments for the port bounce test.
                See [Troubleshooting.port_bounce_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.port_bounce_test) for detailed parameter information.

        Returns:
            (dict): Result of the port bounce test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.port_bounce_test, ports=ports, **kwargs
        )

    def poe_bounce_test(self, ports, **kwargs):
        """Initiates a PoE bounce test on the specified ports.

        Supported device types: cx, aos-s, gateways

        Args:
            ports (list): List of ports to test
            **kwargs (dict, Optional): Optional arguments for the PoE bounce test.
                See [Troubleshooting.poe_bounce_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.poe_bounce_test) for detailed parameter information.

        Returns:
            (dict): Result of the PoE bounce test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.poe_bounce_test, ports=ports, **kwargs
        )

    def arp_test(self):
        """Initiates an ARP table retrieval test on the device.

        Supported device types: aos-s, aps, gateways

        Returns:
            (dict): Result of the ARP test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.retrieve_arp_table_test
        )

    def nslookup_test(self, host, **kwargs):
        """Initiates an NSLOOKUP test on the device.

        Supported device types: aps

        Args:
            host (str): The hostname or IP address to resolve
            **kwargs (dict, Optional): Optional arguments for the NSLOOKUP test.
                See [Troubleshooting.nslookup_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.nslookup_test) for detailed parameter information.

        Returns:
            (dict): Result of the NSLOOKUP test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.nslookup_test, host=host, **kwargs
        )

    def speedtest_test(self, iperf_server_address, **kwargs):
        """Initiates a speed test using the specified iPerf server address.

        Supported device types: aps only

        Args:
            iperf_server_address (str): The IP address or hostname of the iPerf server
            **kwargs (dict, Optional): Optional arguments for the speed test.
                See [Troubleshooting.speedtest_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.speedtest_test) for detailed parameter information.

        Returns:
            (dict): Result of the speed test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.speedtest_test,
            iperf_server_address=iperf_server_address,
            **kwargs,
        )

    def tcp_test(self, host, port, **kwargs):
        """Initiates a TCP test to the specified host and port from the device.

        Supported device types: aps only

        Args:
            host (str): The IP address or hostname to test
            port (int): The port number to test
            **kwargs (dict, Optional): Optional arguments for the TCP test.
                See [Troubleshooting.tcp_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.tcp_test) for detailed parameter information.

        Returns:
            (dict): Result of the TCP test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.tcp_test, host=host, port=port, **kwargs
        )

    def aaa_test(self, radius_server_ip, username, password, **kwargs):
        """Initiates an AAA test with the specified parameters.

        CX devices require auth_method_type as a parameter.
        Supported device types: aps and cx only

        Args:
            radius_server_ip (str): RADIUS server IP address, hostname is valid for APs only
            username (str): Username for authentication
            password (str): Password for authentication
            **kwargs (dict, Optional): Optional arguments specific to device type. See below for details:

                - CX switches - `auth_method_type` (str) is required (`chap` or `pap`), [Troubleshooting.aaa_cx_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.aaa_cx_test)
                  parameters.
                - Access Points - [Troubleshooting.aaa_aps_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.aaa_aps_test) parameters.

        Returns:
            (dict): Result of the AAA test

        Raises:
            ValueError: If device type is unsupported
        """
        self._ensure_materialized()

        if (
            self.device_type == "SWITCH"
            and self._identify_switch_os() == CX_API_ENDPOINT
        ):
            return Troubleshooting.aaa_cx_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                radius_server_ip=radius_server_ip,
                username=username,
                password=password,
                **kwargs,
            )
        elif self.device_type == "ACCESS_POINT":
            return Troubleshooting.aaa_aps_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                radius_server_ip=radius_server_ip,
                username=username,
                password=password,
                **kwargs,
            )
        else:
            raise ValueError(
                f"AAA test is not supported for device type {self.device_type}."
            )

    def cable_test(self, ports, **kwargs):
        """Initiates a Cable test on the specified ports.

        Supported device types: cx, aos-s

        Args:
            ports (list): List of ports to test
            **kwargs (dict, Optional): Optional arguments for the cable test.
                See [Troubleshooting.cable_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.cable_test) for detailed parameter information.

        Returns:
            (dict): Result of the Cable test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.cable_test, ports=ports, **kwargs
        )

    def iperf_test(self, server_address, **kwargs):
        """Initiates an iPerf test using the specified server address.

        Supported device types: gateways only

        Args:
            server_address (str): The IP address or hostname of the iPerf server
            **kwargs (dict, Optional): Optional arguments for the iPerf test.
                See [Troubleshooting.iperf_test()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.iperf_test) for detailed parameter information.

        Returns:
            (dict): Result of the iPerf test
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.iperf_test,
            server_address=server_address,
            **kwargs,
        )

    def list_show_commands(self):
        """Returns most used/top 'show' commands supported on this device.

        Supported device types: aps, gateways, cx, aos-s

        Returns:
            (list or dict): List of show commands organized by category if successful, otherwise full response dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.list_show_commands
        )

    def run_show_commands(self, commands, **kwargs):
        """Runs 'show' command(s) on the device and polls for test result.

        All commands must start with 'show '.

        Supported device types: aps, gateways, cx, aos-s

        Args:
            commands (str or list): Single show command as string (e.g., "show version") or
                list of show commands (e.g., ["show version", "show ip route"]). Max 20 commands.
                All commands must start with 'show '.
            **kwargs (dict, Optional): Optional arguments for the show command test.
                See [Troubleshooting.run_show_command()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.run_show_command) for detailed parameter information.

        Returns:
            (dict): Response from the test results API
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.run_show_commands, commands=commands, **kwargs
        )

    def list_active_tasks(self):
        """Retrieves a list of all active or recently completed asynchronous operations for this device, grouped by test name.

        Results are sorted by startTime in descending order (most recently started first).

        Supported device types: aps, gateways, cx, aos-s

        Returns:
            (dict): Response containing list of active tasks grouped by test name
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.list_active_tasks
        )

    def list_events(self, **kwargs):
        """Retrieves a list of Network Events for this device based on the query parameters provided.

        Supported device types: All (aps, cx, aos-s, gateways)

        Args:
            **kwargs (dict, Optional): Arguments for event listing. See [Troubleshooting.list_events()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.list_events) for all parameters.
                Required parameters: site_id and either duration or both start_at and end_at

        Returns:
            (dict): Response containing events list, count, total, and pagination cursor
        """
        self._ensure_materialized()

        return Troubleshooting.list_events(
            central_conn=self.central_conn,
            context_type=self.device_type,
            context_id=self.serial,
            **kwargs,
        )

    def list_event_filters(self, **kwargs):
        """Retrieves available event filter options for this device.

        Supported device types: All (aps, cx, aos-s, gateways)

        Args:
            **kwargs (dict, Optional): Arguments for event filter listing. See [Troubleshooting.list_event_filters()](troubleshooting.md#pycentral.troubleshooting.troubleshooting.Troubleshooting.list_event_filters) for all parameters.
                Required parameters: site_id and either duration or both start_at and end_at

        Returns:
            (dict): Response containing available event filter options
        """
        self._ensure_materialized()

        return Troubleshooting.list_event_filters(
            central_conn=self.central_conn,
            context_type=self.device_type,
            context_id=self.serial,
            **kwargs,
        )

    def _execute_troubleshooting_command(self, command_method, **kwargs):
        """Executes a troubleshooting command with common setup.

        Args:
            command_method (callable): The troubleshooting method to call
            **kwargs: Additional arguments to pass to the command

        Returns:
            (dict): Result of the troubleshooting command

        Raises:
            ValueError: If method is not supported for device type
        """
        self._ensure_materialized()
        device_type = self._get_effective_device_type()

        method_name = command_method.__name__
        if (
            method_name in TROUBLESHOOTING_METHOD_DEVICE_MAPPING
            and device_type
            not in TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(method_name)
        ):
            raise ValueError(
                f"{method_name} is not supported for device type {device_type}. Supported types are: {TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(method_name)}"
            )
        return command_method(
            central_conn=self.central_conn,
            device_type=device_type,
            serial_number=self.serial,
            **kwargs,
        )

    def _ensure_materialized(self):
        """Ensures the device is materialized before performing operations.

        Raises:
            Exception: If device is not materialized
        """
        if not self.materialized:
            raise Exception(
                "Device is not materialized. Please fetch the device details first."
            )

    def _get_effective_device_type(self):
        """Gets the effective device type, resolving switch OS if needed.

        Returns:
            (str): The effective device type for troubleshooting operations

        Raises:
            ValueError: If device type is unsupported
        """
        device_type = self.device_type

        # Use mapping for direct conversions
        if device_type in DEVICE_TYPE_MAPPING:
            mapped_type = DEVICE_TYPE_MAPPING[device_type]
            if mapped_type is not None:
                return mapped_type
            elif device_type == "SWITCH":
                # Special case: switches require OS identification
                return self._identify_switch_os()

        # Fallback for unsupported device types
        raise ValueError(
            f"Unsupported device type for troubleshooting: {device_type}. "
            f"Supported types are: {', '.join([v for v in DEVICE_TYPE_MAPPING.values() if v is not None] + ['cx', 'aos-s'])}."
        )

    def _identify_switch_os(self):
        """Identifies the switch OS based on device model.

        Returns:
            (str): Switch OS endpoint ("cx" or "aos-s")

        Raises:
            ValueError: If device type is not SWITCH or model is missing/unsupported
        """
        if self.device_type != "SWITCH":
            raise ValueError(
                "This method is only applicable for devices of type 'SWITCH'."
            )

        if not hasattr(self, "model") or not self.model:
            raise ValueError(
                "Device model information is required to identify switch OS."
            )

        prefix = self.model[:1]

        if prefix in SWITCH_OS_MAPPING:
            return SWITCH_OS_MAPPING[prefix]
        else:
            raise ValueError(
                f"Unable to identify switch OS for model '{self.model}'. "
                f"Supported model prefixes: {', '.join(SWITCH_OS_MAPPING.keys())}"
            )
