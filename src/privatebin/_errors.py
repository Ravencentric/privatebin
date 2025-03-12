from __future__ import annotations


class PrivateBinError(Exception):
    """Custom exception for errors related to PrivateBin operations."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
