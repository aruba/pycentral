# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.url_utils import generate_url
from ..exceptions import ParameterError

WEBHOOKS_ENDPOINT = "webhooks"


class Webhooks:
    @staticmethod
    def get_webhooks(central_conn):
        """Retrieve a list of all webhooks.

        This method makes an API call to the following endpoint - `GET network-services/v1/webhooks`

        Args:
            central_conn (NewCentralBase): Central connection object.

        Returns:
            (list): List of webhook objects containing endpoint URL, auth mechanism,
                createdAt, and updatedAt timestamps.

        Raises:
            ParameterError: If central_conn is None.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")

        path = generate_url(WEBHOOKS_ENDPOINT, "services", "v1")
        resp = central_conn.command("GET", path, api_params={})
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving webhooks from {path}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def create_webhook(central_conn, name, url, auth_mechanism=None, subscriptions=None):
        """Create a new webhook.

        This method makes an API call to the following endpoint - `POST network-services/v1/webhooks`

        Args:
            central_conn (NewCentralBase): Central connection object.
            name (str): Webhook name.
            url (str): Receiver endpoint URL.
            auth_mechanism (str, optional): Authentication mechanism for webhook delivery.
            subscriptions (list, optional): List of event type strings to subscribe to.

        Returns:
            (dict): Created webhook object.

        Raises:
            ParameterError: If central_conn is None, name or url are missing or not strings.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not name or not isinstance(name, str):
            raise ParameterError("name is required and must be a non-empty string")
        if not url or not isinstance(url, str):
            raise ParameterError("url is required and must be a non-empty string")

        body = {"name": name, "url": url}
        if auth_mechanism is not None:
            body["authMechanism"] = auth_mechanism
        if subscriptions is not None:
            body["subscriptions"] = subscriptions

        path = generate_url(WEBHOOKS_ENDPOINT, "services", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data=body)
        if resp["code"] not in (200, 201):
            raise Exception(
                f"Error creating webhook: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def get_webhook(central_conn, webhook_id):
        """Retrieve details for a specific webhook.

        This method makes an API call to the following endpoint - `GET network-services/v1/webhooks/{webhook_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            webhook_id (str): Unique identifier of the webhook.

        Returns:
            (dict): Webhook details.

        Raises:
            ParameterError: If central_conn is None or webhook_id is missing or not a string.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not webhook_id or not isinstance(webhook_id, str):
            raise ParameterError("webhook_id is required and must be a non-empty string")

        path = generate_url(f"{WEBHOOKS_ENDPOINT}/{webhook_id}", "services", "v1")
        resp = central_conn.command("GET", path, api_params={})
        if resp["code"] != 200:
            raise Exception(
                f"Error retrieving webhook {webhook_id}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def update_webhook(central_conn, webhook_id, name=None, url=None, auth_mechanism=None, subscriptions=None):
        """Update a webhook using a full replacement (PUT).

        This method makes an API call to the following endpoint - `PUT network-services/v1/webhooks/{webhook_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            webhook_id (str): Unique identifier of the webhook to update.
            name (str, optional): New webhook name.
            url (str, optional): New receiver endpoint URL.
            auth_mechanism (str, optional): New authentication mechanism.
            subscriptions (list, optional): New list of event type strings to subscribe to.

        Returns:
            (dict): Updated webhook object.

        Raises:
            ParameterError: If central_conn is None or webhook_id is missing or not a string.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not webhook_id or not isinstance(webhook_id, str):
            raise ParameterError("webhook_id is required and must be a non-empty string")

        body = {}
        if name is not None:
            body["name"] = name
        if url is not None:
            body["url"] = url
        if auth_mechanism is not None:
            body["authMechanism"] = auth_mechanism
        if subscriptions is not None:
            body["subscriptions"] = subscriptions

        path = generate_url(f"{WEBHOOKS_ENDPOINT}/{webhook_id}", "services", "v1")
        resp = central_conn.command(api_method="PUT", api_path=path, api_data=body)
        if resp["code"] != 200:
            raise Exception(
                f"Error updating webhook {webhook_id}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def patch_webhook(central_conn, webhook_id, **kwargs):
        """Partially update a webhook (PATCH).

        This method makes an API call to the following endpoint - `PATCH network-services/v1/webhooks/{webhook_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            webhook_id (str): Unique identifier of the webhook to patch.
            **kwargs: Arbitrary keyword arguments representing fields to update
                (e.g. name, url, authMechanism, subscriptions).

        Returns:
            (dict): Updated webhook object.

        Raises:
            ParameterError: If central_conn is None or webhook_id is missing or not a string.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not webhook_id or not isinstance(webhook_id, str):
            raise ParameterError("webhook_id is required and must be a non-empty string")

        path = generate_url(f"{WEBHOOKS_ENDPOINT}/{webhook_id}", "services", "v1")
        resp = central_conn.command(api_method="PATCH", api_path=path, api_data=kwargs)
        if resp["code"] != 200:
            raise Exception(
                f"Error patching webhook {webhook_id}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def delete_webhook(central_conn, webhook_id):
        """Delete a webhook.

        This method makes an API call to the following endpoint - `DELETE network-services/v1/webhooks/{webhook_id}`

        Args:
            central_conn (NewCentralBase): Central connection object.
            webhook_id (str): Unique identifier of the webhook to delete.

        Returns:
            (dict): API response confirming deletion.

        Raises:
            ParameterError: If central_conn is None or webhook_id is missing or not a string.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not webhook_id or not isinstance(webhook_id, str):
            raise ParameterError("webhook_id is required and must be a non-empty string")

        path = generate_url(f"{WEBHOOKS_ENDPOINT}/{webhook_id}", "services", "v1")
        resp = central_conn.command(api_method="DELETE", api_path=path)
        if resp["code"] not in (200, 204):
            raise Exception(
                f"Error deleting webhook {webhook_id}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]

    @staticmethod
    def rotate_hmac_key(central_conn, webhook_id):
        """Rotate the HMAC key for a webhook.

        This method makes an API call to the following endpoint - `POST network-services/v1/webhooks/{webhook_id}/hmac-key`

        Args:
            central_conn (NewCentralBase): Central connection object.
            webhook_id (str): Unique identifier of the webhook whose HMAC key to rotate.

        Returns:
            (dict): API response containing the new HMAC key details.

        Raises:
            ParameterError: If central_conn is None or webhook_id is missing or not a string.
        """
        if not central_conn:
            raise ParameterError("central_conn is required")
        if not webhook_id or not isinstance(webhook_id, str):
            raise ParameterError("webhook_id is required and must be a non-empty string")

        path = generate_url(f"{WEBHOOKS_ENDPOINT}/{webhook_id}/hmac-key", "services", "v1")
        resp = central_conn.command(api_method="POST", api_path=path, api_data={})
        if resp["code"] not in (200, 201):
            raise Exception(
                f"Error rotating HMAC key for webhook {webhook_id}: {resp['code']} - {resp['msg']}"
            )
        return resp["msg"]
