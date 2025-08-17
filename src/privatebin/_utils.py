from __future__ import annotations

import json
import mimetypes
import sys
import zlib

from ._enums import Compression


class Compressor:
    """PrivateBin API compatibile compressor."""

    def __init__(self, *, mode: Compression) -> None:
        self.mode = mode

    def compress(self, data: bytes) -> bytes:
        """Compress the input data."""
        match self.mode:
            case Compression.ZLIB:
                # `wbits=-zlib.MAX_WBITS` is required by the PrivateBin API.
                compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
                compressed = compressor.compress(data)
                compressed += compressor.flush()
                return compressed
            case Compression.NONE:
                return data
            case _:
                supported = ", ".join(f"{c.name!r}" for c in Compression)
                msg = f"Unsupported compression mode: {self.mode!r}. Supported modes are: {supported}"
                raise TypeError(msg)

    def decompress(self, data: bytes) -> bytes:
        """Decompress the input data."""
        match self.mode:
            case Compression.ZLIB:
                # `wbits=-zlib.MAX_WBITS` is required by the PrivateBin API.
                decompressor = zlib.decompressobj(wbits=-zlib.MAX_WBITS)
                decompressed = decompressor.decompress(data)
                decompressed += decompressor.flush()
                return decompressed
            case Compression.NONE:
                return data
            case _:
                supported = ", ".join(f"{c.name!r}" for c in Compression)
                msg = f"Unsupported compression mode: {self.mode!r}. Supported modes are: {supported}"
                raise TypeError(msg)


def to_compact_jsonb(obj: object) -> bytes:
    """
    Serialize a Python object to a compact UTF-8 encoded JSON byte string.

    This format removes unnecessary whitespace in separators (`,` and `:`)
    for compatibility with the PrivateBin API and to ensure correct decryption.

    Parameters
    ----------
    obj : object
        The Python object to convert to JSON.

    Returns
    -------
    bytes
        A UTF-8 encoded, compact JSON representation of the object.

    """
    return json.dumps(
        obj,
        # This is important!
        # The default separators add unnecessary whitespace
        # which throws off the decryption later down the line.
        separators=(",", ":"),
    ).encode()


def guess_mime_type(filename: str) -> str:
    """
    Guess the MIME type of a file based on its filename extension.

    If a MIME type can be guessed, it is returned. Otherwise, it defaults to
    'application/octet-stream', which is a generic MIME type for binary data.

    Parameters
    ----------
    filename : str
        The name of the file (including its extension) for which to guess the MIME type.

    Returns
    -------
    str
        The guessed MIME type as a string. Returns 'application/octet-stream'
        if the MIME type cannot be determined.

    References
    ----------
    https://developer.mozilla.org/en-US/docs/Web/HTTP/MIME_types#applicationoctet-stream

    """
    if sys.version_info >= (3, 13):
        guesser = mimetypes.guess_file_type
    else:
        guesser = mimetypes.guess_type

    mimetype, _ = guesser(filename)

    return mimetype if mimetype else "application/octet-stream"


def assert_type(
    obj: object, typ: type[object] | tuple[type[object], ...], /, *, param: str
) -> None:
    """Shortcut for `isinstance(obj, type)` with a nice error message."""
    if not isinstance(obj, typ):
        if isinstance(typ, tuple):
            types = ", ".join(f"{item.__name__!r}" for item in typ)
            expected = f"one of the following types: {types}"
        else:
            expected = f"{typ.__name__!r}"

        msg = f"Parameter '{param}' expected {expected}, but got {type(obj).__name__!r}."
        raise TypeError(msg)
