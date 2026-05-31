import ssl
import websocket
from .events.audit import audit_trail_pb2
from .events.location import location_pb2
from .events.location_analytics import location_analytics_pb2
from .events.geofence import geofence_pb2
from .events.event import event_pb2
from google.protobuf.json_format import MessageToDict
import threading
import signal

VERSION = "v1alpha1"
# Central-mandated ping settings (not user-configurable)
_PING_INTERVAL = 10  # seconds between keep-alive pings
_PING_TIMEOUT = 5  # seconds to wait for a pong response

# Supported Events and their corresponding endpoints and decoders
SUPPORTED_EVENTS = {
    "audit-trail-events": audit_trail_pb2.AuditTrail,
    "location": location_pb2.StreamLocationMessage,
    "rssi-events": location_analytics_pb2.RssiEvent,
    "geofence": geofence_pb2.StreamGeofenceMessage,
}


class Streaming:
    """
    Minimal WebSocket streaming client for HPE Aruba Networking Central.

    Responsibilities:
        - Build the WSS URL for the selected streaming endpoint.
        - Maintain a single WebSocket connection with optional auto-reconnect.
        - Decode protobuf payloads and deliver them to a user callback.
        - Allow graceful stop and cleanup of the WebSocket connection.

    Args:
        central_conn (NewCentralBase): Central connection object, used for
            tokens, base URL and logging.
        event (str): Streaming event name. Must be one of the keys in
            SUPPORTED_EVENTS (for example, "audit-trail-events").
        reconnect_delay (int, optional): Delay in seconds before attempting
            to reconnect after an unexpected disconnection. Defaults to 5.
        max_retries (int|None, optional): Maximum number of reconnection
            attempts after an unexpected disconnection. ``None`` (default)
            means retry indefinitely.
        filters (str|list[str], optional): Either a single filter string or a list of filter strings.
            If a list is provided, its elements will be joined with commas to form the header value.

    Raises:
        ValueError: If an unsupported event is provided or filters are of an unexpected type.
    """

    def __init__(
        self,
        central_conn,
        event,
        reconnect_delay=5,
        max_retries=None,
        filters=None,
    ):
        self.central_conn = central_conn
        # cache the commonly used app route and token key to simplify lookups
        self.app_route = self.central_conn._app_routes["new_central"]
        self.token_key = self.app_route["token_key"]
        if event not in SUPPORTED_EVENTS:
            raise ValueError(
                f"Unsupported event: {event}. Supported events: {list(SUPPORTED_EVENTS.keys())}"
            )
        self.endpoint = event
        self.decoder = SUPPORTED_EVENTS[event]
        self.reconnect_delay = reconnect_delay
        self.max_retries = max_retries
        self.logger = central_conn.logger
        self.ws = None
        self.user_callback = None

        self.stop_event = threading.Event()  # Thread-safe stop flag
        self._original_sigint = None

        self.filters = self._normalize_filters(filters)

    @staticmethod
    def _normalize_filters(filters):
        """Validate and normalise the filters argument to a comma-separated
        string, or None when no filters are requested.

        Args:
            filters (str|list[str]|None): Raw filter value supplied by
                the caller.

        Returns:
            str|None: Normalised filter string or None.

        Raises:
            ValueError: For unsupported types or non-string list elements.
        """
        if filters is None:
            return None
        if isinstance(filters, str):
            return filters
        if isinstance(filters, list):
            if not all(isinstance(f, str) for f in filters):
                raise ValueError("All filter values must be strings.")
            return ",".join(filters)
        raise ValueError("Filters must be a string or a list of strings.")

    def _build_headers(self):
        """Assemble the HTTP headers required for the WebSocket handshake.

        Returns:
            list[str]: Header strings ready for websocket.WebSocketApp.
        """
        token = self.central_conn.token_info["new_central"]["access_token"]
        headers = [f"Authorization: Bearer {token}"]
        if self.filters:
            headers.append(f"event-types: {self.filters}")
        return headers

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages.

        The raw message is first parsed as a CloudEvent protobuf and then
        decoded using the event-specific protobuf decoder. The decoded
        message is converted to a dict and passed to the user callback
        if provided, otherwise logged.

        Args:
            ws (websocket.WebSocketApp): WebSocket instance (unused).
            message (bytes): Raw protobuf-encoded message payload.
        """
        event_data = event_pb2.CloudEvent()
        event_data.ParseFromString(message)

        decoded_message = self.decoder()
        decoded_message.ParseFromString(event_data.proto_data.value)
        json_message = MessageToDict(
            decoded_message, preserving_proto_field_name=True
        )
        if self.user_callback:
            try:
                self.user_callback(json_message)
            except Exception as callback_error:
                self.logger.error(
                    f"Callback raised an error: {callback_error}"
                )
        else:
            self.logger.info(f"{json_message}")

    def _on_error(self, ws, error):
        """Handle WebSocket errors.

        * HTTP 401: attempts a token refresh via the Central connection;
          stops streaming if the refresh fails.
        * Other HTTP errors (403, 404, …): unrecoverable — stops streaming
          immediately so the reconnect loop does not retry indefinitely.
        * All other errors (network resets, timeouts, …): logged and left
          for the reconnect loop to handle transparently.

        Args:
            ws (websocket.WebSocketApp): WebSocket instance (unused).
            error (Exception|str): Error raised by the WebSocket client.
        """
        self.logger.error(f"WebSocket error: {error}")
        if isinstance(error, websocket.WebSocketBadStatusException):
            if error.status_code == 401:
                try:
                    self.central_conn.handle_expired_token("new_central")
                    self.logger.info("Token refreshed. Will reconnect.")
                except Exception as refresh_error:
                    self.logger.error(f"Token refresh failed: {refresh_error}")
                    self.stop_event.set()
            else:
                # Non-401 HTTP rejection (e.g. 403 Forbidden, 404 Not Found).
                # Retrying will not fix the problem; stop immediately.
                self.logger.error(
                    f"Unrecoverable HTTP error {error.status_code}. "
                    f"Response body: {error.resp_body}. Stopping."
                )
                self.stop_event.set()
        # For all other error types (OSError, network reset, etc.) the
        # reconnect loop in stream() will handle retrying automatically.

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close events.

        Args:
            ws (websocket.WebSocketApp): WebSocket instance (unused).
            close_status_code (int|None): WebSocket close status code.
            close_msg (str|None): Close reason/message from server.
        """
        self.logger.info(
            f"Disconnected (code: {close_status_code}, msg: {close_msg})"
        )

    def _on_open(self, ws):
        """Handle WebSocket open events.

        Args:
            ws (websocket.WebSocketApp): WebSocket instance.
        """
        self.logger.info(
            f"Connection established. Listening for {self.endpoint}..."
        )
        if self.filters:
            self.logger.info(f"Applied filters: {self.filters}")

    def _get_wss_url(self):
        """Build the WebSocket Secure (WSS) URL for the configured event.

        The URL is constructed using the Central base URL from the
        connection object and the event-specific endpoint.

        Returns:
            str: Fully qualified WSS URL for the streaming endpoint.
        """
        base_url = self.central_conn.token_info["new_central"][
            "base_url"
        ].rstrip("/")
        # Strip any scheme so we can always prefix with wss://
        host = base_url.replace("https://", "", 1).replace("http://", "", 1)
        return f"wss://{host}/network-services/{VERSION}/{self.endpoint}"

    def stream(self, callback=None):
        """Start streaming messages for the configured event.

        This method establishes the WebSocket connection, listens for
        messages, and optionally auto-reconnects on unexpected closure
        until `stop()` is called or a fatal error occurs.

        Args:
            callback (callable, optional): Function to be invoked for each
                decoded message. It must accept a single argument
                (dict) representing the decoded protobuf message.
                If not provided, decoded messages are logged.

        Raises:
            KeyboardInterrupt: If interrupted by the user (Ctrl+C) while
                streaming in a foreground loop.
        """
        self.user_callback = callback
        self.stop_event.clear()

        self._setup_signal_handler()

        retry_count = 0
        try:
            while not self.stop_event.is_set():
                try:
                    url = self._get_wss_url()
                    self.ws = websocket.WebSocketApp(
                        url,
                        header=self._build_headers(),
                        on_open=self._on_open,
                        on_close=self._on_close,
                        on_error=self._on_error,
                        on_message=self._on_message,
                    )

                    self.logger.info(f"Connecting to {url}...")
                    self.ws.run_forever(
                        sslopt={"cert_reqs": ssl.CERT_NONE},
                        ping_interval=_PING_INTERVAL,
                        ping_timeout=_PING_TIMEOUT,
                    )

                    if self.stop_event.is_set():
                        break

                    retry_count += 1
                    if self.max_retries is not None and retry_count >= self.max_retries:
                        self.logger.error(
                            f"Max retries ({self.max_retries}) reached. Stopping."
                        )
                        self.stop_event.set()
                        break

                    self.logger.info(
                        f"Connection closed. Reconnecting in {self.reconnect_delay}s… "
                        f"(attempt {retry_count}"
                        + (f"/{self.max_retries}" if self.max_retries is not None else "")
                        + ")"
                    )
                    if self.stop_event.wait(timeout=self.reconnect_delay):
                        break

                except Exception as e:
                    self.logger.error(
                        f"Unexpected error in streaming loop: {e}"
                    )
                    if self.ws:
                        self.ws.close()
                    retry_count += 1
                    if self.max_retries is not None and retry_count >= self.max_retries:
                        self.logger.error(
                            f"Max retries ({self.max_retries}) reached. Stopping."
                        )
                        self.stop_event.set()
                        break
                    if self.stop_event.wait(timeout=self.reconnect_delay):
                        break
        finally:
            self._restore_signal_handler()
            self._cleanup()

    def stop(self):
        """Request the streaming loop to stop and close the WebSocket.

        This method can be called from another thread or from within
        the user callback to stop streaming gracefully.
        """
        self.logger.info("Stop requested.")
        self.stop_event.set()
        self._cleanup()

    def _cleanup(self):
        """Clean up WebSocket resources after streaming stops.

        Ensures the WebSocket is closed and internal references are
        reset. This method is idempotent.
        """
        if self.ws:
            try:
                self.ws.close()
            finally:
                self.ws = None
        self.logger.info("Cleanup complete.")

    def _setup_signal_handler(self):
        """Set up signal handler for graceful shutdown on Ctrl+C."""

        if threading.current_thread() is not threading.main_thread():
            return

        def signal_handler(signum, frame):
            self.logger.info("Received interrupt signal. Stopping...")
            self.stop()

        self._original_sigint = signal.signal(signal.SIGINT, signal_handler)

    def _restore_signal_handler(self):
        """Restore the original signal handler."""
        if threading.current_thread() is not threading.main_thread():
            return
        if self._original_sigint is not None:
            signal.signal(signal.SIGINT, self._original_sigint)
            self._original_sigint = None
