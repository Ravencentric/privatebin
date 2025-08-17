from __future__ import annotations

import base64
import re
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, TypedDict
from urllib.parse import urljoin

import msgspec

from privatebin._enums import Compression, Formatter, PrivateBinEncryptionSetting
from privatebin._errors import PrivateBinError
from privatebin._utils import guess_mime_type, to_compact_jsonb

if TYPE_CHECKING:
    from collections.abc import Iterator
    from os import PathLike

    from typing_extensions import NotRequired, Self


class RawPasteContent(TypedDict):
    """
    Represents the raw paste content.
    This is what we POST to PrivateBin after attaching the necessary metadata
    and this is what we get back from PrivateBin after the necessary post-processing.

    ```json
    {
        "paste": "Hello World!",
        "attachment": "data:text/plain;base64,VGhpcyBpcyBhbiBhdHRhY2htZW50Lg==",
        "attachment_name": "hello.txt"
    }
    ```
    """

    paste: str
    attachment: NotRequired[str]
    attachment_name: NotRequired[str]


class CipherParameters(NamedTuple):
    """
    Parameters defining the cipher configuration for encrypting PrivateBin pastes.

    Notes
    -----
    The PrivateBin API returns the `salt` and `initialization_vector`
    as base64 encoded strings. msgspec automatically handles this by
    decoding the base64 strings back into raw bytes when parsing the API response.
    Therefore, when we access `cipher_parameters.salt` and
    `cipher_parameters.initialization_vector`, we are working with the
    *raw bytes* of the `salt` and `initialization_vector`.

    Examples
    --------
    ```python
    import base64
    import os

    import msgspec


    class ApiResponse(msgspec.Struct):
        iv: bytes
        salt: bytes


    raw_iv_bytes = os.urandom(16)
    raw_salt_bytes = os.urandom(8)

    base64_iv_str = base64.b64encode(raw_iv_bytes).decode()
    base64_salt_str = base64.b64encode(raw_salt_bytes).decode()

    api_response_dict = {"iv": base64_iv_str, "salt": base64_salt_str}
    parsed_response = msgspec.convert(api_response_dict, type=ApiResponse)

    assert parsed_response.iv == raw_iv_bytes == base64.b64decode(base64_iv_str)
    assert parsed_response.salt == raw_salt_bytes == base64.b64decode(base64_salt_str)
    ```

    """

    initialization_vector: bytes
    """The initialization vector (IV) as Base64 encoded bytes."""
    salt: bytes
    """The salt as Base64 encoded bytes."""
    iterations: int
    """The number of iterations for the key derivation function (PBKDF2HMAC)."""
    key_size: int
    """The size of the encryption key in bits."""
    tag_size: int
    """The size of the authentication tag in bits for AESGCM."""
    algorithm: Literal["aes"]
    """The encryption algorithm. Currently the only supported value is 'aes'."""
    mode: Literal["gcm"]
    """The encryption mode of operation. Currently the only supported value is 'gcm'."""
    compression: Compression
    """The compression algorithm used before encryption."""

    @classmethod
    def new(
        cls,
        *,
        initialization_vector: bytes,
        salt: bytes,
        compression: Compression = Compression.ZLIB,
    ) -> Self:
        """
        Create a new CipherParameters instance with default encryption settings.

        Parameters
        ----------
        initialization_vector : bytes
            The initialization vector used for encryption. Must be provided as raw bytes.
        salt : bytes
            The salt used for key derivation. Must be provided as raw bytes.
        compression : Compression, optional
            Compression algorithm to use before encryption.

        Returns
        -------
        Self

        Examples
        --------
        >>> iv = os.urandom(16)
        >>> salt = os.urandom(8)
        >>> params = CipherParameters.new(initialization_vector=iv, salt=salt)
        >>> params.algorithm
        'aes'
        >>> params.compression
        <Compression.ZLIB: 'zlib'>

        """
        return cls(
            initialization_vector=initialization_vector,
            salt=salt,
            iterations=PrivateBinEncryptionSetting.ITERATIONS,
            key_size=PrivateBinEncryptionSetting.KEY_SIZE,
            tag_size=PrivateBinEncryptionSetting.TAG_SIZE,
            algorithm="aes",
            mode="gcm",
            compression=compression,
        )


class AuthenticatedData(NamedTuple):
    """Encapsulates all authenticated data associated with a PrivateBin paste."""

    cipher_parameters: CipherParameters
    """Cipher parameters used for encryption."""
    formatter: Formatter
    """The formatting option for the paste content."""
    open_discussion: bool
    """Flag indicating if open discussions are enabled for this paste."""
    burn_after_reading: bool
    """Flag indicating if the paste should be burned after the first read."""

    @classmethod
    def new(  # noqa: PLR0913
        cls,
        *,
        initialization_vector: bytes,
        salt: bytes,
        formatter: Formatter = Formatter.PLAIN_TEXT,
        open_discussion: bool = False,
        burn_after_reading: bool = False,
        compresssion: Compression = Compression.ZLIB,
    ) -> Self:
        """
        Create a new AuthenticatedData instance with specified parameters.

        Parameters
        ----------
        initialization_vector : bytes
            The initialization vector used for encryption. Must be provided as raw bytes.
        salt : bytes
            The salt used for key derivation. Must be provided as raw bytes.
        formatter : Formatter, optional
            The format of the paste content.
        open_discussion : bool, optional
            Whether discussions are allowed on the paste.
        burn_after_reading : bool, optional
            Whether the paste should be deleted after first read.
        compresssion : Compression, optional
            Compression algorithm to use for cipher parameters.

        Returns
        -------
        Self

        Examples
        --------
        >>> import os
        >>> iv = os.urandom(16)
        >>> salt = os.urandom(8)
        >>> data = AuthenticatedData.new(initialization_vector=iv, salt=salt, formatter=Formatter.MARKDOWN, open_discussion=True)
        >>> data.formatter
        <Formatter.MARKDOWN: 'markdown'>
        >>> data.open_discussion
        True
        >>> data.cipher_parameters.algorithm
        'aes'

        """
        return cls(
            cipher_parameters=CipherParameters.new(
                initialization_vector=initialization_vector, salt=salt, compression=compresssion
            ),
            formatter=formatter,
            open_discussion=open_discussion,
            burn_after_reading=burn_after_reading,
        )

    def to_serializable_tuple(self) -> tuple[tuple[object, ...], str, int, int]:
        """
        Convert to a basic tuple that can be serialized to JSON.
        It base64 encodes byte-like cipher parameters for safe transport in JSON
        and converts boolean flags to integers (required by PrivateBin API).

        Returns
        -------
        tuple[tuple[object, ...], str, int, int]

        """
        cipher_parameters = tuple(
            base64.b64encode(param).decode() if isinstance(param, bytes) else param
            for param in self.cipher_parameters
        )
        return (
            cipher_parameters,
            self.formatter,
            int(self.open_discussion),
            int(self.burn_after_reading),
        )

    def to_bytes(self) -> bytes:
        """
        Serialize to a JSON-encoded byte string.

        Returns
        -------
        bytes
            A JSON-encoded byte string representing the `AuthenticatedData` instance.

        """
        return to_compact_jsonb(self.to_serializable_tuple())


class MetaData(msgspec.Struct, frozen=True, kw_only=True):
    """Metadata received with a PrivateBin paste from the server."""

    time_to_live: timedelta | None = None
    """
    Time duration remaining until paste expiration, 
    as reported by the server. `None` means the paste will not expire.
    """


class PasteJsonLD(msgspec.Struct, frozen=True, kw_only=True):
    """
    Represents a paste GET response from the PrivateBin API (v2).

    Notes
    -----
    - API Version: Only the v2 API is supported (PrivateBin >= 1.3).
    - Comment Handling: Paste comments are *not* supported and are currently discarded.

    References
    ----------
    - https://raw.githubusercontent.com/PrivateBin/PrivateBin/master/js/paste.jsonld
    - https://github.com/PrivateBin/PrivateBin/wiki/API#as-of-version-13

    Examples
    --------
    Example of a typical JSON response structure parsed by this class:

    ```python
    {
    "status": 0,
    "id": "4e7cea11af458924",
    "url": "/?4e7cea11af458924?4e7cea11af458924",
    "adata": [
        [
        "GEEM/99wIW5yItxLXOCRAQ==",  # <--- Base64 encoded initialization vector
        "d8v8piD9qto=",  # <--- Base64 encoded salt
        100000,  # <--- Iterations
        256,  # <--- Key size
        128,  # <--- Tag size
        "aes",  # <--- Algorithm
        "gcm",  # <--- Mode
        "zlib"  # <--- Compression
        ],
        "plaintext",  # <--- Formatter
        0,  # <--- Open discussion
        0  # <--- Burn after reading
    ],
    "meta": {
        "time_to_live": 86315
    },
    "v": 2,
    "ct": "RgE133BlXs5fjuv0DWboLHKR3WaZPsgszQemDujTJkPprvgIFpqaBLEN",  # <--- Base64 encoded ciphertext
    "comments": [],
    "comment_count": 0,
    "comment_offset": 0,
    "@context": "?jsonld=paste"
    }
    ```

    """

    status: Literal[0]
    """Status code of the response, must be 0."""
    id: str
    """Unique identifier of the paste."""
    url: str
    """URL path to access the paste."""
    adata: AuthenticatedData
    """Authenticated data containing encryption and formatting parameters."""
    meta: MetaData
    """Metadata associated with the paste."""
    v: Literal[2]
    """Version number of the PrivateBin API. Must be `2` for v2 API compatibility."""
    ct: bytes
    """Ciphertext: Encrypted content of the paste."""

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        """
        Create a new instance from an API response.

        Parameters
        ----------
        response : dict[str, Any]
            A dictionary representing the JSON response from the PrivateBin API.

        Returns
        -------
        Self

        Raises
        ------
        PrivateBinError
            If the API response status is not `0` (success) or if the API version is not `2`.

        """
        if response.get("status") != 0:
            # {"status":1, "message": "[errormessage]"}
            msg = response.get("message", "Failed to retrieve paste.")
            raise PrivateBinError(msg)

        if response.get("v") != 2:  # noqa: PLR2004
            msg = f"Only the v2 API is supported (PrivateBin >= 1.3). Got API version: {response.get('v', 'UNKNOWN')}"
            raise PrivateBinError(msg)

        # Possible values:
        # - [] (empty list) - Will not expire
        # - {"time_to_live": 12345} - Will expire in 12345 seconds
        if not response.get("meta"):
            # The API uses an empty list in 'meta' to mean the data won't expire.
            # The `MetaData` class needs 'meta' to be a dictionary with 'time_to_live'.
            # So we turn the API's empty list into {'time_to_live': None}
            # so `MetaData` can correctly parse it.
            response["meta"] = {"time_to_live": None}

        # PrivateBin API declares `open_discussion` and `burn_after_reading` (in `AuthenticatedData.cipher_parameters`)
        # as booleans, but its response contains them as integers (0 or 1).
        # `strict=False` allows msgspec to coerce these integers into booleans.
        return msgspec.convert(response, cls, strict=False)


class JsonStruct(msgspec.Struct, frozen=True, kw_only=True):
    @classmethod
    def from_json(cls, data: str, /) -> Self:
        """
        Create an instance of this class from a JSON string.

        Parameters
        ----------
        data : str
            JSON string representing the Paste instance.

        Returns
        -------
        Self

        """
        return msgspec.json.decode(data, type=cls)

    def to_json(self, *, indent: int = 2) -> str:
        """
        Serialize this instance into a JSON string.

        Parameters
        ----------
        indent : int, optional
            Number of spaces for indentation.
            Set to 0 for a single line with spacing,
            or negative to minimize size by removing extra whitespace.

        Returns
        -------
        str
            JSON string representing the Paste.

        """
        jsonified = msgspec.json.encode(self)
        return msgspec.json.format(jsonified, indent=indent).decode()


class Attachment(JsonStruct, frozen=True, kw_only=True):
    """Represents an attachment with its content and name."""

    name: str
    """The name of the attachment."""
    content: bytes
    """The binary content of the attachment."""

    @classmethod
    def from_file(cls, file: str | PathLike[str], *, name: str | None = None) -> Self:
        """
        Create an `Attachment` instance from a file path.

        If a name is not provided, the filename from the path is used as the attachment name.

        Parameters
        ----------
        file : str | PathLike[str]
            Path to the file from which to create the attachment.
        name : str | None, optional
            The desired name for the attachment. If `None`, the filename from `file` is used.

        Returns
        -------
        Self

        Raises
        ------
        FileNotFoundError
            If the provided `file` path does not exist or is not a file.

        """
        file = Path(file).expanduser().resolve()

        if not file.is_file():
            raise FileNotFoundError(file)

        filename = name if name else file.name
        content = file.read_bytes()

        return cls(content=content, name=filename)

    @classmethod
    def from_data_url(cls, *, url: str, name: str) -> Self:
        """
        Create an Attachment from a [data URL][Data URL].

        [Data URL]: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data

        Parameters
        ----------
        url : str
            Attachment content as a data URL.
        name : str
            The desired name for the attachment.

        Returns
        -------
        Self

        Raises
        ------
        ValueError
            If the provided `url` is not a data URL.

        """
        # https://regex101.com/r/Wiu431/1
        pattern = r"^data:(?P<mimetype>.+);base64,(?P<data>.+)$"
        match = re.fullmatch(pattern, url)

        if match is None:
            truncated = url[:50] + "... (TRUNCATED)" if len(url) > 50 else url  # noqa: PLR2004
            msg = (
                "Paste has an invalid or unsupported attachment. "
                f"Expected a data URL: 'data:<mimetype>;base64,<data>', got: {truncated!r}"
            )
            raise ValueError(msg)

        data = match.group("data")
        content = base64.b64decode(data)

        return cls(content=content, name=name)

    def to_data_url(self) -> str:
        """
        Convert the Attachment's binary content to a [data URL][Data URL].

        [Data URL]: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data

        Returns
        -------
        str
            A data URL representing the attachment content.

        """
        encoded = base64.b64encode(self.content).decode()
        mimetype = guess_mime_type(self.name)
        return f"data:{mimetype};base64,{encoded}"


class Paste(JsonStruct, frozen=True, kw_only=True):
    """Represents a PrivateBin paste."""

    id: str
    """Unique identifier for the paste."""
    text: str
    """The decrypted text content of the paste."""
    attachment: Attachment | None
    """Attachment associated with the paste, if any."""
    formatter: Formatter
    """Formatting option applied to the paste content."""
    open_discussion: bool
    """Indicates if open discussions are enabled for this paste."""
    burn_after_reading: bool
    """Indicates if the paste is set to be burned after the first read."""
    time_to_live: timedelta | None
    """Time duration for which the paste is set to be stored, if any."""


class PrivateBinUrl(JsonStruct, frozen=True, kw_only=True):
    """Represents a PrivateBin URL."""

    server: str
    """The base server URL of the PrivateBin instance."""
    id: str
    """The unique paste ID. This identifies the specific paste on the server."""
    passphrase: str
    """The decryption passphrase. This is needed to decrypt and view encrypted pastes."""

    def unmask(self) -> str:
        """
        Explicitly convert this instance into a complete, unmasked URL string.

        This method behaves differently from implicit Python string conversions
        like `print(url)`, or f-strings (`f"{url}"`).

        -  `unmask()` returns the full, unmasked URL with the sensitive passphrase.
        -  Implicit conversions (`print()`, f-strings, etc.) return a masked URL for safety.

        Call `unmask()` when you explicitly need the full, working URL, for example, to:

        -  Open the URL in a browser.
        -  Pass the URL to a function that requires the unmasked passphrase.

        Returns
        -------
        str
            The full, unmasked PrivateBin URL.

        Examples
        --------
        >>> url = PrivateBinUrl(server="https://example.privatebin.com/", id="pasteid", passphrase="secret")
        >>> print(url)  # Implicit string conversion - masked URL
        'https://example.privatebin.com/?pasteid#********'
        >>> f"{url}"  # Implicit string conversion in f-string - masked URL
        'https://example.privatebin.com/?pasteid#********'
        >>> url.unmask()
        'https://example.privatebin.com/?pasteid#secret'

        """
        return urljoin(self.server, f"/?{self.id}#{self.passphrase}")

    @classmethod
    def parse(cls, url: str | PrivateBinUrl | PasteReceipt, /) -> Self:
        """
        Parse a URL-like object into a `PrivateBinUrl` instance.

        Parameters
        ----------
        url : str | PrivateBinUrl | PasteReceipt
            The URL-like object to parse.

        Returns
        -------
        Self

        Raises
        ------
        ValueError
            If the provided 'url' string is not in the expected format.
        TypeError
            If the provided 'url' is not in the expected type.

        """
        match url:
            case str():
                try:
                    server, id_passphrase = url.strip().split("?")
                    id, passphrase = id_passphrase.split("#")

                    # The leading hyphen is a visual cue for "burn-after-reading" pastes.
                    # This code removes it because it's not part of the actual passphrase
                    # and would cause decryption to fail. Removing it also ensures that
                    # pastes with and without the hyphen are treated as identical.
                    passphrase = passphrase.removeprefix("-")

                    return cls(server=server, id=id, passphrase=passphrase)
                except ValueError:
                    msg = (
                        "Invalid PrivateBin URL format. "
                        "URL should be like: https://examplebin.net/?pasteid#passphrase. "
                        f"Got: {url!r}"
                    )
                    raise ValueError(msg) from None
            case PrivateBinUrl():
                return cls(server=url.server, id=url.id, passphrase=url.passphrase)
            case PasteReceipt():
                url = url.url
                return cls(server=url.server, id=url.id, passphrase=url.passphrase)
            case _:
                msg = f"Parameter 'url' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got {type(url).__name__!r}."
                raise TypeError(msg)

    def __str__(self) -> str:
        """
        Return a URL-like string representation that is safe to print or log.
        The decryption passphrase is replaced with `********`
        to prevent accidental exposure.

        Examples
        --------
        >>> url = PrivateBinUrl(server="https://example.com/privatebin", id="pasteid", passphrase="secret")
        >>> str(url)
        'https://example.com/privatebin/?pasteid#********'

        """
        return self.unmask().replace(self.passphrase, "********")

    def __repr__(self) -> str:
        """
        Return a string representation that is safe to print or log.
        The decryption passphrase is replaced with `********`
        to prevent accidental exposure.
        """
        return f"{self.__class__.__name__}(server={self.server!r}, id={self.id!r}, passphrase='********')"

    def __rich_repr__(self) -> Iterator[tuple[object, object]]:  # pragma: no cover
        """
        Override the default [rich repr protocol][0] implemented by [msgspec.Struct][1]
        to behave similarly to `__repr__`.

        [0]: https://rich.readthedocs.io/en/stable/pretty.html#rich-repr-protocol
        [1]: https://jcristharif.com/msgspec/structs.html
        """
        yield "server", self.server
        yield "id", self.id
        yield "passphrase", "********"


class PasteReceipt(JsonStruct, frozen=True, kw_only=True):
    """Represents the result of a paste creation."""

    url: PrivateBinUrl
    """The URL of the newly created paste."""
    delete_token: str
    """The token required to delete the paste."""

    def __repr__(self) -> str:
        """
        Return a string representation that is safe to print or log.
        The decryption passphrase and the delete token are replaced
        with `********` to prevent accidental exposure.
        """
        return f"{self.__class__.__name__}(url={self.url!r}, delete_token='********')"

    def __rich_repr__(self) -> Iterator[tuple[object, object]]:  # pragma: no cover
        """
        Override the default [rich repr protocol][0] implemented by [msgspec.Struct][1]
        to behave similarly to `__repr__`.

        [0]: https://rich.readthedocs.io/en/stable/pretty.html#rich-repr-protocol
        [1]: https://jcristharif.com/msgspec/structs.html
        """
        yield "url", self.url
        yield "delete_token", "********"
