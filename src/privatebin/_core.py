from __future__ import annotations

import base64
import json
from collections.abc import Iterable
from types import NoneType
from typing import TYPE_CHECKING, Any

import cryptography.exceptions
import httpx2

from privatebin._base58 import b58decode, b58encode
from privatebin._crypto import decrypt, encrypt
from privatebin._enums import (
    Compression,
    EncryptionSpec,
    Expiration,
    Feature,
    Formatter,
)
from privatebin._errors import PrivateBinDecryptionError, PrivateBinServerError
from privatebin._models import (
    Attachment,
    AuthenticatedData,
    Paste,
    PasteJsonLD,
    PasteReceipt,
    PrivateBinUrl,
    RawPasteContent,
)
from privatebin._url import pb_urljoin
from privatebin._utils import Compressor, assert_type, to_compact_jsonb
from privatebin._version import __version__

if TYPE_CHECKING:
    from typing_extensions import Self

    from privatebin._protocols import HttpClientProtocol


class PrivateBin:
    def __init__(
        self,
        server: str,
        *,
        client: HttpClientProtocol | None = None,
    ) -> None:
        """
        Client for interacting with PrivateBin's v2 API (PrivateBin >= 1.3).

        Parameters
        ----------
        server : str
            URL of the PrivateBin server.
        client : HttpClientProtocol | None, optional
            An existing HTTP client instance to be used for requests.
            If `None`, a new `httpx2.Client` is created. In either case,
            `PrivateBin` takes ownership of the client and will close it
            when the `PrivateBin` instance is closed or exits its context
            manager.

            `httpx2.Client` is an implementation detail and should not be
            relied upon. The client only needs to implement
            `HttpClientProtocol`, and the internal HTTP client implementation
            may change in the future.

        Examples
        --------
        Basic usage to instantiate a PrivateBin client:

        ```python
        with PrivateBin("https://myprivatebin.example.org/") as client:
            paste = client.get(id="pasteid", passphrase="secret")
            print(paste.text)
        ```

        """
        assert_type(server, str, param="server")
        self._server = server
        self._client = (
            httpx2.Client(
                headers={
                    "User-Agent": f"privatebin/{__version__} (https://pypi.org/project/privatebin/)"
                }
            )
            if client is None
            else client
        )
        self._client.headers.update({"X-Requested-With": "JSONHttpRequest"})

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @property
    def server(self) -> str:
        """
        URL of the PrivateBin instance.

        Examples
        --------
        >>> client = PrivateBin("https://myprivatebin.example.org/")
        >>> client.server
        'https://myprivatebin.example.org/'

        """
        return self._server

    def get(self, *, id: str, passphrase: str, password: str | None = None) -> Paste:
        """
        Retrieve and decrypt a paste from PrivateBin.

        Parameters
        ----------
        id : str
            The unique identifier of the paste to retrieve.
        passphrase : str
            The decryption passphrase for the paste, encoded in Base58 format as part of the URL.
        password : str, optional
            Password to decrypt the paste if it was created with one.

        Returns
        -------
        Paste
            A `Paste` object containing the decrypted text, attachment (if any), and metadata.

        Raises
        ------
        PrivateBinServerError
            If the server returns an error for the paste.
        PrivateBinDecryptionError
            If the paste cannot be decrypted with the given passphrase or password.

        Examples
        --------
        ```python
        from privatebin import PrivateBin

        with PrivateBin("https://myprivatebin.example.org/") as pb:
            paste = pb.get(id="pasteid", passphrase="secret")
            print(paste.text)
            for attachment in paste.attachments:
                print(f"Attachment name: {attachment.name}")
        ```

        """
        assert_type(id, str, param="id")
        assert_type(passphrase, str, param="passphrase")
        assert_type(password, (str, NoneType), param="password")

        encoded_password = password.encode() if password else b""

        # The leading hyphen is a visual cue for "burn-after-reading" pastes.
        # This code removes it because it's not part of the actual passphrase
        # and would cause decryption to fail.
        cleaned_passphrase = passphrase.removeprefix("-")

        # Passphrase is a base58 encoded string,
        # so we need to decode it.
        decoded_passphrase = b58decode(cleaned_passphrase)

        url = pb_urljoin(self.server, id)
        response = self._client.get(url)
        response.raise_for_status()
        paste = PasteJsonLD.from_response(response.json())
        cipher_parameters = paste.adata.cipher_parameters

        try:
            decrypted = decrypt(
                data=paste.ct,
                length=cipher_parameters.key_size // 8,
                salt=cipher_parameters.salt,
                iterations=cipher_parameters.iterations,
                key_material=decoded_passphrase + encoded_password,
                initialization_vector=cipher_parameters.initialization_vector,
                associated_data=paste.adata.to_bytes(),
            )
        except cryptography.exceptions.InvalidTag as exc:
            msg = "Failed to decrypt paste. Check the passphrase and password."
            raise PrivateBinDecryptionError(msg) from exc

        decompressed = Compressor(mode=cipher_parameters.compression).decompress(decrypted)
        finalized: RawPasteContent = json.loads(decompressed)

        match finalized:
            case {"paste": str(text), "attachment": str(url), "attachment_name": str(name)}:
                attachments = (Attachment.from_data_url(url=url, name=name),)

            case {"paste": str(text), "attachment": list(urls), "attachment_name": list(names)}:
                attachments = tuple(
                    Attachment.from_data_url(url=url, name=name)
                    for url, name in zip(urls, names, strict=True)
                )

            case {"paste": str(text)}:
                attachments = ()

            case _ as unreachable:
                msg = f"Unexpected PrivateBin paste payload: {unreachable!r}"
                raise PrivateBinDecryptionError(msg)

        return Paste(
            id=paste.id,
            text=text,
            attachments=attachments,
            formatter=paste.adata.formatter,
            feature=paste.adata.feature,
            time_to_live=paste.meta.time_to_live,
        )

    def create(
        self,
        text: str,
        *,
        attachments: Attachment | Iterable[Attachment] | None = None,
        password: str | None = None,
        feature: Feature | None = None,
        expiration: Expiration = Expiration.ONE_WEEK,
        formatter: Formatter = Formatter.PLAIN_TEXT,
        compression: Compression = Compression.ZLIB,
    ) -> PasteReceipt:
        """
        Create a new paste on PrivateBin.

        Parameters
        ----------
        text : str
            The text content of the paste.
        attachments : Attachment | Iterable[Attachment], optional
            An attachment or iterable of attachments to include with the paste.
        password : str, optional
            A password to encrypt the paste with an additional layer of security.
            If provided, users will need this password in addition to the passphrase to decrypt the paste.
        feature : Feature | None, optional
            The feature to apply to the paste.
        expiration : Expiration, optional
            The desired expiration time for the paste.
        formatter : Formatter, optional
            The formatting option for the paste content.
        compression : Compression, optional
            The compression algorithm to use for the paste data.

        Returns
        -------
        PasteReceipt
            A `PasteReceipt` object containing the URL to access the newly created paste,
            and the delete token.

        Raises
        ------
        PrivateBinServerError
            If the server refuses the request.
        TypeError
            If provided 'text' is not a `str`.

        Examples
        --------
        Create a simple paste with default settings:

        ```python
        from privatebin import PrivateBin

        with PrivateBin("https://myprivatebin.example.org/") as pb:
            paste = pb.create("Hello, PrivateBin!")
            print(f"Paste created at: {paste.url}")
        ```

        Create a paste with Markdown formatting and burn-after-reading:

        ```python
        from privatebin import Feature, Formatter, PrivateBin

        with PrivateBin("https://myprivatebin.example.org/") as pb:
            paste = pb.create(
                text="This *is* **markdown** formatted text.",
                formatter=Formatter.MARKDOWN,
                feature=Feature.BURN_AFTER_READING
            )
            print(f"Markdown paste URL: {paste.url}")
        ```

        Create a password-protected paste with an attachment:

        ```python
        from privatebin import Attachment, PrivateBin

        with PrivateBin("https://myprivatebin.example.org/") as pb:
            attachment = Attachment.from_file("path/to/your/file.txt")
            paste = pb.create(
                text="This paste has a password and an attachment.",
                password="supersecret",
                attachments=attachment
            )
            print(f"Password-protected paste URL: {paste.url}")
        ```

        """
        assert_type(text, str, param="text")
        assert_type(password, (str, NoneType), param="password")
        assert_type(feature, (Feature, NoneType), param="feature")
        assert_type(expiration, Expiration, param="expiration")
        assert_type(formatter, Formatter, param="formatter")
        assert_type(compression, Compression, param="compression")

        data: RawPasteContent = {"paste": text}

        match attachments:
            case None:
                pass

            case Attachment():
                data["attachment"] = attachments.to_data_url()
                data["attachment_name"] = attachments.name

            case Iterable():
                data["attachment"] = []
                data["attachment_name"] = []

                for attachment in attachments:
                    if not isinstance(attachment, Attachment):
                        msg = (
                            "Parameter 'attachments' expected an iterable of 'Attachment' objects."
                        )
                        raise TypeError(msg)

                    data["attachment"].append(attachment.to_data_url())
                    data["attachment_name"].append(attachment.name)

            case _:
                raise TypeError(
                    "Parameter 'attachments' expected 'Attachment', "
                    "'Iterable[Attachment]', or 'NoneType'."
                )

        initialization_vector = EncryptionSpec.initialization_vector()
        salt = EncryptionSpec.salt()
        passphrase = EncryptionSpec.passphrase()

        encoded_password = password.encode() if password else b""

        encoded_data = to_compact_jsonb(data)
        compressed_data = Compressor(mode=compression).compress(encoded_data)

        adata = AuthenticatedData.new(
            initialization_vector=initialization_vector,
            salt=salt,
            formatter=formatter,
            feature=feature,
            compression=compression,
        )

        encrypted = encrypt(
            data=compressed_data,
            length=EncryptionSpec.KEY_SIZE // 8,
            salt=salt,
            iterations=EncryptionSpec.ITERATIONS,
            key_material=passphrase + encoded_password,
            initialization_vector=initialization_vector,
            associated_data=adata.to_bytes(),
        )

        payload = {
            "v": 2,
            "adata": adata.to_serializable_tuple(),
            "ct": base64.b64encode(encrypted).decode(),
            "meta": {"expire": expiration},
        }

        # Success: {"status": 0, "id": "blah", "url": "/?blah", "deletetoken": "blah"}
        # Failure: {"status": 1, "message": "[errormessage]"}
        posted = self._client.post(url=self.server, json=payload)
        posted.raise_for_status()
        response: dict[str, Any] = posted.json()

        if response.get("status") != 0:
            msg = response.get("message", "Failed to create paste.")
            raise PrivateBinServerError(msg)

        return PasteReceipt(
            url=PrivateBinUrl(
                server=self.server,
                id=response["id"],
                passphrase=b58encode(passphrase),
            ),
            delete_token=response["deletetoken"],
        )

    def delete(self, *, id: str, delete_token: str) -> None:
        """
        Delete a paste from PrivateBin using its ID and delete token.

        Parameters
        ----------
        id : str
            The unique identifier of the paste to delete.
        delete_token : str
            The deletion token associated with the paste.

        Raises
        ------
        PrivateBinServerError
            If the server refuses the request.

        Examples
        --------
        ```python
        from privatebin import PrivateBin

        with PrivateBin("https://myprivatebin.example.org/") as pb:
            paste = pb.create(text="This paste will be deleted.")
            print(f"Paste URL: {paste.url}")
            pb.delete(id=paste.url.id, delete_token=paste.delete_token)
            print(f"Paste with ID '{paste.url.id}' deleted.")
        ```

        """
        assert_type(id, str, param="id")
        assert_type(delete_token, str, param="delete_token")

        payload = {"pasteid": id, "deletetoken": delete_token}

        # Success: {"status":0, "id": "[pasteID]"}
        # Failure: {"status":1, "message": "[errormessage]"}
        posted = self._client.post(self.server, json=payload)
        posted.raise_for_status()
        response: dict[str, Any] = posted.json()

        if response.get("status") != 0:
            msg = response.get("message", "Failed to delete paste.")
            raise PrivateBinServerError(msg)

    def close(self) -> None:
        """Close the underlying HTTP client session."""
        self._client.close()
