# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.exceptions.pycentral_error import PycentralError


class LoginError(PycentralError):
    """Exception raised when login or authentication fails.

    This exception is raised when authentication to Central fails,
    typically due to invalid credentials, expired tokens, or network issues.

    Attributes:
        base_msg (str): The base error message for this exception type.
        message (str): Detailed error message describing the login failure.
        status_code (int): HTTP status code associated with the login failure, if available.

    Example:
        ```python
        >>> raise LoginError(msg, status_code)
        LoginError: LOGIN ERROR - Invalid client or client credentials. for
        new_central. Provide valid client_id and client_secret to create an
        access token. (status_code=401)
        ```
    """

    base_msg = "LOGIN ERROR"

    def __init__(self, message, status_code=None, *details):
        self.status_code = status_code

        parts = [self.base_msg]
        if message:
            parts.append(str(message))
        if details:
            parts.extend(str(d) for d in details)

        self.message = " - ".join(parts)

    def __str__(self):
        if self.status_code is not None:
            return f"{self.message} (status_code={self.status_code})"
        return self.message
