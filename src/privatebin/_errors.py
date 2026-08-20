from __future__ import annotations


class PrivateBinError(Exception):
    """Base for errors that occur while handling a paste."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class PrivateBinServerError(PrivateBinError):
    """Raised when the server refuses the request."""


class PrivateBinDecryptionError(PrivateBinError):
    """Raised when a paste cannot be decrypted."""
