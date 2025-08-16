from __future__ import annotations

import json
import mimetypes
import sys
import zlib


class Zlib:
    """
    Provides PrivateBin API compatibile zlib compression and decompression.

    This class ensures data is compressed and decompressed using `wbits=-zlib.MAX_WBITS`,
    omitting headers and checksums as required by the PrivateBin API.
    """

    def __init__(self, data: bytes) -> None:
        """
        Initialize Zlib with data.

        Parameters
        ----------
        data : bytes
            The data to be compressed or decompressed.

        """
        self.data = data
        self.wbits = -zlib.MAX_WBITS

    def compress(self) -> bytes:
        """
        Return zlib compressed data.

        Returns
        -------
        bytes
            Compressed data.

        """
        compressor = zlib.compressobj(wbits=self.wbits)
        compressed = compressor.compress(self.data)
        compressed += compressor.flush()
        return compressed

    def decompress(self) -> bytes:
        """
        Return zlib decompressed data.

        Returns
        -------
        bytes
            Decompressed data.

        """
        decompressor = zlib.decompressobj(wbits=self.wbits)
        decompressed = decompressor.decompress(self.data)
        decompressed += decompressor.flush()
        return decompressed


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
