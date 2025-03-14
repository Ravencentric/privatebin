from __future__ import annotations

from privatebin._core import PrivateBin
from privatebin._enums import Compression, Expiration, Formatter
from privatebin._errors import PrivateBinError
from privatebin._models import Attachment, Paste, PrivateBinUrl
from privatebin._wrapper import create, delete, get

__version__ = "0.1.0"

__all__ = (
    "Attachment",
    "Compression",
    "Expiration",
    "Formatter",
    "Paste",
    "PrivateBin",
    "PrivateBinError",
    "PrivateBinUrl",
    "create",
    "delete",
    "get",
)
