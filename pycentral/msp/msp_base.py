# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

"""MSP-aware extension of NewCentralBase.

Use :class:`MSPBase` instead of :class:`NewCentralBase` when operating
as a Managed Service Provider (MSP).  The class inherits all base functionality
and adds :meth:`get_tenant_connection`, which performs a tenant-specific token
exchange and returns an isolated :class:`TenantBase` instance scoped to
that tenant's environment.

When the tenant connection's access token expires, it automatically renews the
parent MSP token first and then re-exchanges it for a fresh tenant-scoped token,
keeping the entire chain in sync through a single renewal path.

Example::

    from pycentral import MSPBase

    msp = MSPBase(
        token_info={
            "unified": {
                "client_id": "<client-id>",
                "client_secret": "<client-secret>",
                "workspace_id": "<workspace-id>",
                "cluster_name": "US-WEST-5",
            }
        }
    )

    # Obtain a scoped connection for a specific tenant
    tenant_conn = msp.get_tenant_connection(tenant_workspace_id="<tenant-workspace-id>")
    # Use tenant_conn.command(...) for all tenant-scoped Central API calls
"""

from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError, InvalidClientError
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

from ..base import NewCentralBase
from ..exceptions import LoginError
from ..utils import AUTHENTICATION
from .tenant_base import TenantBase

class MSPBase(NewCentralBase):
    """
    NewCentralBase subclass with MSP tenant token-exchange support.

    All constructor arguments are identical to NewCentralBase.
    MSP mode exclusively uses "unified" credentials so that both GLP and
    Central API calls share a single token, while per-tenant access is
    obtained via get_tenant_connection().

    Tenant connections are cached internally: calling get_tenant_connection()
    with the same tenant_workspace_id multiple times always returns the same
    TenantBase instance without re-running the token exchange.
    Use close_tenant_connection() to explicitly close a single tenant connection,
    or close() (inherited) to close the MSP connection and all cached tenant connections.

    Args:
        token_info (dict or str): Token information dict or path to a YAML/JSON
            credentials file. See NewCentralBase for full details.
        logger (logging.Logger, optional): External logger. Defaults to None.
        log_level (str, optional): Log level string. Defaults to "INFO".
        enable_scope (bool, optional): Whether to initialise scope management. Defaults to False.
    """

    def __init__(self, token_info, logger=None, log_level="INFO", enable_scope=False):
        # Tenant connection cache: {tenant_workspace_id: TenantBase}
        # Initialised before super().__init__ so it exists if any subclass hook
        # were to call get_tenant_connection during initialisation.
        self._tenant_connections: dict = {}
        super().__init__(
            token_info=token_info,
            logger=logger,
            log_level=log_level,
            enable_scope=enable_scope,
        )

    def _get_msp_access_token(self):
        """
        Return the current MSP-level Central access token.

        Reads access_token from the unified token_info entry, which is
        the only supported token management method for MSP mode.

        Returns:
            (str or None): The current MSP access token for Central calls.

        Note:
            Internal SDK function
        """

        return self.token_info["unified"].get("access_token")

    def _exchange_tenant_token(self, tenant_workspace_id: str) -> str:
        """
        Exchange the current MSP access token for a tenant-scoped token (RFC 8693).

        If the MSP token is expired, it is renewed automatically and the exchange
        is retried once. Both get_tenant_connection() and
        TenantBase.handle_expired_token() delegate here.

        Args:
            tenant_workspace_id (str): The tenant's GLP workspace ID, used as the
                audience in the token exchange URL.

        Returns:
            (str): The tenant-scoped Central access token.

        Raises:
            LoginError: If MSP token renewal or the token exchange fails.

        Note:
            Internal SDK function
        """
        client_id, client_secret = self._return_client_credentials("unified")
        client = BackendApplicationClient(client_id)
        client.grant_type = "urn:ietf:params:oauth:grant-type:token-exchange"
        oauth = OAuth2Session(client=client)
        auth = HTTPBasicAuth(client_id, client_secret)
        token_url = f"{AUTHENTICATION['OAUTH_GLOBAL']}/{tenant_workspace_id}/token"
        fetch_kwargs = dict(
            token_url=token_url,
            auth=auth,
            subject_token_type="urn:ietf:params:oauth:token-type:access_token",
        )

        for attempt in range(2):
            try:
                token = oauth.fetch_token(
                    subject_token=self._get_msp_access_token(), **fetch_kwargs
                )
                self.logger.debug(
                    "Tenant token exchanged for tenant_workspace_id='%s' (expires_in=%s)",
                    tenant_workspace_id,
                    token.get("expires_in"),
                )
                return token["access_token"]
            except (TokenExpiredError, InvalidClientError):
                if attempt >= 1:
                    msg = (
                        f"Failed to exchange tenant token for tenant_workspace_id='{tenant_workspace_id}' "
                        "after MSP token renewal."
                    )
                    self.logger.error(msg)
                    raise LoginError(msg)
                self.logger.info(
                    f"MSP token expired during tenant exchange for '{tenant_workspace_id}'. "
                    "Renewing and retrying..."
                )
                self.create_token("unified")
            except Exception as e:
                msg = f"Failed to exchange tenant token for tenant_workspace_id='{tenant_workspace_id}': {e}"
                self.logger.error(msg)
                raise LoginError(msg)

    def get_tenant_connection(
        self, tenant_name=None, tenant_workspace_id=None
    ) -> TenantBase:
        """
        Obtain a tenant-scoped connection for the given tenant.

        Returns a cached TenantBase if one already exists for
        tenant_workspace_id. Otherwise performs the token exchange, creates a
        new connection, caches it, and returns it.

        Token expiry is handled automatically: when a cached connection receives
        a 401, it renews the MSP parent token and re-exchanges it for a fresh
        tenant token without any additional caller action.

        Args:
            tenant_name (str, optional): The display name of the MSP tenant.
            tenant_workspace_id (str, optional): The tenant's GLP workspace ID,
                used as the subject in the token exchange request. Find this in
                the GLP tenant list response (``tenantId`` field).

        Returns:
            (TenantBase): A connection instance scoped to the specified
                tenant's Central environment. Use its command() method for all
                tenant-scoped API calls. The same object is returned on subsequent
                calls with the same tenant_workspace_id.

        Raises:
            ValueError: If neither tenant_name nor tenant_workspace_id is provided,
                or if Central is not configured on this MSP instance (no cluster_name
                or base_url under "unified", and no standalone "glp" entry).
            LoginError: If MSP token renewal or the token exchange fails.
        """
        if tenant_workspace_id is None and tenant_name is None:
            raise ValueError("Either 'tenant_workspace_id' or 'tenant_name' must be provided.")

        if tenant_name:
            tenant_workspace_id = self.get_tenant_id(tenant_name)

        if type(tenant_workspace_id) is not str:
            raise ValueError("tenant_workspace_id must be a string.")
        # Normalize tenant_workspace_id by removing dashes as per GLP API requirements
        tenant_workspace_id = tenant_workspace_id.replace("-", "")
        # Return cached connection if it already exists
        if tenant_workspace_id in self._tenant_connections:
            self.logger.debug(
                f"Returning cached tenant connection for tenant_workspace_id='{tenant_workspace_id}'"
            )
            return self._tenant_connections[tenant_workspace_id]

        self.logger.info(f"Creating new tenant connection for tenant_workspace_id='{tenant_workspace_id}'")

        # Exchange the MSP token for a tenant-scoped token
        tenant_access_token = self._exchange_tenant_token(tenant_workspace_id)

        # Build a minimal token_info for the tenant connection using unified mode
        # (no client credentials needed — renewal delegates back to this MSP instance).
        tenant_token_info = {
            "unified": {
                "glp_base_url": self.token_info["unified"].get("glp_base_url"),
                "base_url": self.token_info["unified"].get("base_url"),
                "access_token": tenant_access_token,
            },
        }

        conn = TenantBase(
            token_info=tenant_token_info,
            msp_parent=self,
            tenant_workspace_id=tenant_workspace_id,
            logger=self.logger,
        )
        self._tenant_connections[tenant_workspace_id] = conn
        self.logger.info(f"Tenant connection for '{tenant_workspace_id}' established and cached.")
        return conn

    def close_tenant_connection(self, tenant_workspace_id: str) -> None:
        """
        Close and evict the cached connection for a specific tenant.

        Releases the underlying HTTP client resources for the given tenant and
        removes it from the cache. The next call to get_tenant_connection() with
        the same tenant_workspace_id will perform a fresh token exchange.

        Args:
            tenant_workspace_id (str): The tenant's GLP workspace ID whose
                cached connection should be closed.

        Raises:
            KeyError: If no cached connection exists for tenant_workspace_id.
        """
        tenant_workspace_id = tenant_workspace_id.replace("-", "")
        if tenant_workspace_id not in self._tenant_connections:
            raise KeyError(
                f"No cached tenant connection found for tenant_workspace_id='{tenant_workspace_id}'. "
                "Use get_tenant_connection() to create one first."
            )
        conn = self._tenant_connections.pop(tenant_workspace_id)
        try:
            conn.close()
        except Exception as err:
            self.logger.debug(
                f"Error closing HTTP clients for tenant '{tenant_workspace_id}': {err}"
            )
        self.logger.info(f"Tenant connection for '{tenant_workspace_id}' closed.")

    def close(self) -> None:
        """
        Close the MSP connection and all cached tenant connections.

        Closes every cached TenantBase first, then closes the
        MSP-level HTTP clients inherited from NewCentralBase.
        """
        for tenant_workspace_id in list(self._tenant_connections):
            try:
                self._tenant_connections[tenant_workspace_id].close()
            except Exception as err:
                self.logger.debug(
                    f"Error closing tenant connection '{tenant_workspace_id}' during MSP close: {err}"
                )
        self._tenant_connections.clear()
        super().close()

    def get_tenant_id(self, tenant_name):
        """
        Resolve a tenant display name to its GLP workspace ID.

        Queries the GLP MSP tenants API and returns the workspace ID for the
        given tenant name. This workspace ID is required for the token exchange
        performed by get_tenant_connection().

        Args:
            tenant_name (str): The display name of the tenant to resolve.

        Returns:
            (str): The tenant's GLP workspace ID.

        Raises:
            ValueError: If the tenant_name cannot be resolved to a workspace ID.
        """
        api_path = "workspaces/v1/msp-tenants"
        api_method = "GET"
        safe_name = tenant_name.replace("'", "''")
        api_params = {"filter": f"workspaceName eq '{safe_name}'"}
        response = self.command(
            api_method=api_method,
            api_path=api_path,
            app_name="glp",
            api_params=api_params,
        )
        if response["code"] != 200:
            raise ValueError(
                f"Failed to retrieve tenants: {response.get('msg', 'No error message provided')}"
            )
        response_msg = response.get("msg", {})
        tenant = response_msg.get("items", [])

        if not tenant:
            raise ValueError(f"No tenant found with name '{tenant_name}'")
        if len(tenant) > 1:
            raise ValueError(f"Multiple tenants found with name '{tenant_name}'")
        tenant_workspace_id = tenant[0].get("id")
        return tenant_workspace_id
