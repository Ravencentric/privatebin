from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from privatebin._core import PrivateBin
    from privatebin._enums import Compression, Expiration, Feature, Formatter
    from privatebin._errors import (
        PrivateBinDecryptionError,
        PrivateBinError,
        PrivateBinServerError,
    )
    from privatebin._models import Attachment, Paste, PasteReceipt, PrivateBinUrl
    from privatebin._version import __version__
    from privatebin._wrapper import create, delete, get


__all__: Final = (
    "Attachment",
    "Compression",
    "Expiration",
    "Feature",
    "Formatter",
    "Paste",
    "PasteReceipt",
    "PrivateBin",
    "PrivateBinDecryptionError",
    "PrivateBinError",
    "PrivateBinServerError",
    "PrivateBinUrl",
    "__version__",
    "create",
    "delete",
    "get",
)


def __getattr__(name: str) -> Any:
    """Poor man's lazy imports because we can't use PEP-810 anytime soon."""
    import importlib

    imports = {
        "PrivateBin": "privatebin._core",
        "Attachment": "privatebin._models",
        "Paste": "privatebin._models",
        "PasteReceipt": "privatebin._models",
        "PrivateBinUrl": "privatebin._models",
        "Compression": "privatebin._enums",
        "Expiration": "privatebin._enums",
        "Feature": "privatebin._enums",
        "Formatter": "privatebin._enums",
        "PrivateBinError": "privatebin._errors",
        "PrivateBinDecryptionError": "privatebin._errors",
        "PrivateBinServerError": "privatebin._errors",
        "create": "privatebin._wrapper",
        "delete": "privatebin._wrapper",
        "get": "privatebin._wrapper",
        "__version__": "privatebin._version",
    }

    module = imports.get(name)
    if module is None:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    return getattr(importlib.import_module(module), name)


def __dir__() -> list[str]:
    return list(__all__)
