from __future__ import annotations

import base64
import re
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, NamedTuple
from urllib.parse import urljoin

from pydantic import (
    Base64Bytes,
    BaseModel,
    ConfigDict,
    field_serializer,
    field_validator,
)

from privatebin._enums import Compression, Formatter, PrivateBinEncryptionSetting
from privatebin._errors import PrivateBinError
from privatebin._utils import guess_mime_type, to_compact_json

if TYPE_CHECKING:
    from os import PathLike

    from typing_extensions import Self


class FrozenModel(BaseModel):
    """Frozen model."""

    model_config = ConfigDict(frozen=True)


class CipherParameters(NamedTuple):
    """
    Parameters defining the cipher configuration for encrypting PrivateBin pastes.

    Base64Bytes Behavior:
    ---------------------
    The PrivateBin API returns the `salt` and `initialization_vector`
    as base64 encoded strings. Pydantic's `Base64Bytes` type automatically
    handles this by decoding the base64 strings back into raw bytes when
    parsing the API response. Therefore, when we access `cipher_parameters.salt`
    and `cipher_parameters.initialization_vector`, we are working with the
    *raw bytes* of the `salt` and `initialization_vector`.

    Example: Base64Bytes Decoding
    -----------------------------
    ```python
    import base64
    import os
    from pydantic import Base64Bytes, BaseModel

    class ApiResponse(BaseModel):
        iv: Base64Bytes
        salt: Base64Bytes

    raw_iv_bytes = os.urandom(16)
    raw_salt_bytes = os.urandom(8)

    base64_iv_str = base64.b64encode(raw_iv_bytes).decode()
    base64_salt_str = base64.b64encode(raw_salt_bytes).decode()

    api_response_dict = {"iv": base64_iv_str, "salt": base64_salt_str}
    parsed_response = ApiResponse.model_validate(api_response_dict)

    assert parsed_response.iv == raw_iv_bytes == base64.b64decode(base64_iv_str)
    assert parsed_response.salt == raw_salt_bytes == base64.b64decode(base64_salt_str)
    ```
    """

    initialization_vector: Base64Bytes
    """The initialization vector (IV) as Base64 encoded bytes."""
    salt: Base64Bytes
    """The salt as Base64 encoded bytes."""
    iterations: int
    """The number of iterations for the key derivation function (PBKDF2HMAC)."""
    key_size: int
    """The size of the encryption key in bits."""
    tag_size: int
    """The size of the authentication tag in bits for AESGCM."""
    algorithm: Literal["aes"]
    """The encryption algorithm. Currently the only support value is 'aes'."""
    mode: Literal["gcm"]
    """The encryption mode of operation. Currently the only support value is 'gcm'."""
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

    def to_tuple(self) -> tuple[tuple[object, ...], str, int, int]:
        """
        Convert to a basic tuple that can be serialized to JSON.
        It base64 encodes byte-like cipher parameters for safe transport in JSON
        and converts boolean flags to integers (required by PrivateBin API).

        Returns
        -------
        tuple[tuple[object, ...], str, int, int]

        """
        cipher_parameters = [
            base64.b64encode(param).decode() if isinstance(param, bytes) else param
            for param in self.cipher_parameters
        ]
        return (
            tuple(cipher_parameters),
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
        return to_compact_json(self.to_tuple()).encode()


class MetaData(FrozenModel):
    """Metadata received with a PrivateBin paste from the server."""

    time_to_live: timedelta | None = None
    """
    Time duration remaining until paste expiration, 
    as reported by the server. `None` means the paste will not expire.
    """


class PasteJsonLD(FrozenModel):
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

    ```json
    {
    "status": 0,
    "id": "4e7cea11af458924",
    "url": "/?4e7cea11af458924?4e7cea11af458924",
    "adata": [
        [
        "GEEM/99wIW5yItxLXOCRAQ==",
        "d8v8piD9qto=",
        100000,
        256,
        128,
        "aes",
        "gcm",
        "zlib"
        ],
        "plaintext",
        0,
        0
    ],
    "meta": {
        "time_to_live": 86315
    },
    "v": 2,
    "ct": "RgE133BlXs5fjuv0DWboLHKR3WaZPsgszQemDujTJkPprvgIFpqaBLEN",
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
    ct: Base64Bytes
    """Ciphertext: Base64 encoded encrypted content of the paste."""

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

        return cls.model_validate(response)

    @field_validator("meta", mode="before")
    @classmethod
    def normalize_meta(cls, value: Any) -> Any:
        """
        Normalize the 'meta' field from the API response before validation.

        Normalization Process:
            - If 'meta' is an empty list `[]`, it is converted into an empty `MetaData` instance.
            - If 'meta' is already a dictionary, it is used as is for creating a `MetaData` instance.
        """
        return value if value else MetaData()


class Attachment(FrozenModel):
    """Represents an attachment with its content and name."""

    content: bytes
    """The binary content of the attachment."""
    name: str
    """The name of the attachment."""

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
    def from_base64_data_url(cls, *, content: str, name: str) -> Self:
        """
        Create an Attachment from a base64 encoded data URL string.

        Decodes a base64 encoded data URL string, expected to be in the format
        ``data:<mimetype>;base64,<data>``, and creates an `Attachment`.

        Parameters
        ----------
        content : str
            Base64 encoded string representing the attachment content,
            including the data URL prefix.
        name : str
            The desired name for the attachment.

        Returns
        -------
        Self

        Raises
        ------
        ValueError
            If the provided `content` string does not match the expected base64 data URL format.

        """
        # https://regex101.com/r/Wiu431/1
        pattern = r"^data:(?P<mimetype>.+);base64,(?P<data>.+)$"
        match = re.fullmatch(pattern, content)

        if match is None:
            truncated = content[:50] + "... (TRUNCATED)" if len(content) > 50 else content  # noqa: PLR2004
            msg = (
                "Paste has an invalid or unsupported attachment. "
                f"Expected format: 'data:<mimetype>;base64,<data>', got: {truncated!r}"
            )
            raise ValueError(msg)

        data = match.group("data")
        decoded = base64.b64decode(data)

        return cls(content=decoded, name=name)

    def to_base64_data_url(self) -> str:
        """
        Convert the Attachment's binary content to a base64 encoded data URL string.

        Encodes the attachment's content to base64 and formats it as a data URL
        string, including a MIME type guessed from the attachment's name.
        If a MIME type cannot be guessed, it defaults to `application/octet-stream`.

        Returns
        -------
        str
            A base64 encoded data URL string representing the attachment content.

        """
        encoded = base64.b64encode(self.content).decode()
        mimetype = guess_mime_type(self.name)
        return f"data:{mimetype};base64,{encoded}"

    @field_serializer("content", when_used="json")
    def _serialize_content_to_base64_data_url(self, content: bytes) -> str:
        """
        Serialize the attachment's content to a base64 data URL when exporting to JSON.

        The `content` parameter in the method signature only exists because
        it is required by Pydantic's `@field_serializer` decorator. We don't actually use it.

        Returns
        -------
        str
            A base64 encoded data URL string representing the attachment content.

        """
        return self.to_base64_data_url()


class Paste(FrozenModel):
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


class PrivateBinUrl(FrozenModel):
    """Represents a parsed PrivateBin URL, including its components and delete token."""

    server: str
    """The base server URL of the PrivateBin instance."""
    id: str
    """The unique paste ID. This identifies the specific paste on the server."""
    passphrase: str
    """The decryption passphrase. This is needed to decrypt and view encrypted pastes."""
    delete_token: str
    """The delete token. Authorizes deletion of the paste."""

    def to_str(self) -> str:
        """
        Explicitly convert the instance into a complete, unmasked URL string.

        This method behaves differently from implicit Python string conversions
        like `print(url)`, or f-strings (`f"{url}"`).

        -  `to_str()` returns the full, unmasked URL with the sensitive passphrase.
        -  Implicit conversions (`print()`, f-strings, etc.) return a masked URL for safety.

        Call `to_str()` when you explicitly need the full, working URL, for example, to:

        -  Open the URL in a browser.
        -  Pass the URL to a function that requires the unmasked passphrase.

        Returns
        -------
        str
            The full, unmasked PrivateBin URL.

        Examples
        --------
        >>> url = PrivateBinUrl(server="https://example.privatebin.com/", id="pasteid", passphrase="secret", delete_token="deltoken")
        >>> url.to_str()
        'https://example.privatebin.com/?pasteid#secret'
        >>> print(url)  # Implicit string conversion - masked URL
        'https://example.privatebin.com/?pasteid#********'
        >>> f"{url}"  # Implicit string conversion in f-string - masked URL
        'https://example.privatebin.com/?pasteid#********'

        """
        return urljoin(self.server, f"/?{self.id}#{self.passphrase}")

    def __str__(self) -> str:
        """
        Return a URL string, masking the passphrase for security in logs.

        Provides a string representation of the URL that is safe to print or log.
        The decryption passphrase is replaced with `********` to prevent accidental exposure.

        Returns
        -------
        str
            A URL string with the passphrase replaced by `********`.

        Examples
        --------
        >>> url = PrivateBinUrl(server="https://example.com/privatebin", id="pasteid", passphrase="secret", delete_token="deltoken")
        >>> str(url)
        'https://example.com/privatebin/?pasteid#********'

        """
        return self.to_str().replace(self.passphrase, "********")

    def __repr__(self) -> str:
        """
        Return a string representation of the PrivateBinUrl instance.

        Returns
        -------
        str
            A string representation of the `PrivateBinUrl` instance, with a masked passphrase.

        """
        return self.__str__()
