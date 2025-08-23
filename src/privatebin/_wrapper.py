from __future__ import annotations

from urllib.parse import urlparse

from privatebin._core import PrivateBin
from privatebin._enums import Compression, Expiration, Formatter
from privatebin._models import Attachment, Paste, PasteReceipt, PrivateBinUrl


def get(url: str | PrivateBinUrl | PasteReceipt, *, password: str | None = None) -> Paste:
    """
    Retrieve and decrypt a paste from a PrivateBin URL.

    Parameters
    ----------
    url : str | PrivateBinUrl | PasteReceipt
        The URL of the PrivateBin paste.
    password : str, optional
        Password to decrypt the paste if it was created with one.

    Returns
    -------
    Paste
        A `Paste` object containing the decrypted text, attachment (if any), and metadata.

    Raises
    ------
    PrivateBinError
        If there is an error retrieving or decrypting the paste from the server.
    ValueError
        If the provided 'url' string is not in the expected format.
    TypeError
        If the provided 'url' is not in the expected type.

    Examples
    --------
    ```python
    import privatebin

    paste = privatebin.get("https://privatebin.net/?pasteid#passphrase")
    print(paste.text)
    ```

    For password-protected pastes:

    ```python
    import privatebin

    paste = privatebin.get("https://privatebin.net/?pasteid#passphrase", password="secret")
    print(paste.text)
    ```

    """
    url = PrivateBinUrl.parse(url)
    with PrivateBin(url.server) as client:
        return client.get(id=url.id, passphrase=url.passphrase, password=password)


def create(  # noqa: PLR0913
    text: str,
    *,
    server: str | PrivateBinUrl | PasteReceipt = "https://privatebin.net/",
    attachment: Attachment | None = None,
    password: str | None = None,
    burn_after_reading: bool = False,
    open_discussion: bool = False,
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
    server : str | PrivateBinUrl | PasteReceipt, optional
        The base URL of the PrivateBin instance to use.
    attachment : Attachment, optional
        An attachment to include with the paste.
    password : str, optional
        A password to encrypt the paste with an additional layer of security.
        If provided, users will need this password in addition to the passphrase to decrypt the paste.
    burn_after_reading : bool, optional
        Set to `True` if the paste should be automatically deleted after the first view.
    open_discussion : bool, optional
        Set to `True` to enable open discussions/comments on the paste.
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
    PrivateBinError
        - If `burn_after_reading` and `open_discussion` are both set to `True`.
        - If there is an error during paste creation on PrivateBin.
    TypeError
        If the provided 'url' is not in the expected type.

    Examples
    --------
    Create a simple paste on the default PrivateBin instance:

    ```python
    paste = privatebin.create("Hello, PrivateBin!")
    print(f"Paste URL: {paste.url}")
    ```

    Create a paste on a custom PrivateBin server with Markdown formatting and burn-after-reading:

    ```python
    import privatebin
    from privatebin import Formatter

    paste = privatebin.create(
        text="This *is* **markdown** formatted text.",
        server="https://myprivatebin.example.org/",
        formatter=Formatter.MARKDOWN,
        burn_after_reading=True
    )
    print(f"Markdown paste URL: {paste.url}")
    ```

    Create a password-protected paste with an attachment:

    ```python
    import privatebin
    from privatebin import Attachment

    attachment = Attachment.from_file("path/to/your/file.txt")

    paste = privatebin.create(
        text="This paste has a password and an attachment.",
        password="supersecret",
        attachment=attachment
    )

    print(f"Password-protected paste URL: {paste.url}")
    ```

    """
    match server:
        case str():
            _server = server
        case PrivateBinUrl():
            _server = server.server
        case PasteReceipt():
            _server = server.url.server
        case _:
            msg = f"Parameter 'server' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got {type(server).__name__!r}."
            raise TypeError(msg)

    with PrivateBin(_server) as client:
        return client.create(
            text=text,
            attachment=attachment,
            password=password,
            burn_after_reading=burn_after_reading,
            open_discussion=open_discussion,
            expiration=expiration,
            formatter=formatter,
            compression=compression,
        )


def delete(url: str | PrivateBinUrl | PasteReceipt, *, delete_token: str) -> None:
    """
    Delete a paste from PrivateBin using its URL and delete token.

    Parameters
    ----------
    url : str | PrivateBinUrl | PasteReceipt
        The URL of the PrivateBin paste, with or without the passphrase.
    delete_token : str
        The delete token associated with the paste.

    Raises
    ------
    PrivateBinError
        If there is an error deleting the paste on PrivateBin.
    ValueError
        If the provided 'url' string is not in the expected format.
    TypeError
        If the provided 'url' is not in the expected type.

    Examples
    --------
    ```python
    import privatebin

    paste = privatebin.create(text="This paste will be deleted.")
    privatebin.delete(paste, delete_token=paste.delete_token)
    print(f"Paste with URL '{paste.url}' deleted.")
    ```

    """
    if isinstance(url, str):
        parsed = urlparse(url)
        if not (parsed.scheme and parsed.netloc and parsed.query):
            msg = "Invalid PrivateBin URL format. URL should be like: https://examplebin.net/?pasteid."
            raise ValueError(msg)
        server = f"{parsed.scheme}://{parsed.netloc}"
        id = parsed.query
    else:
        url = PrivateBinUrl.parse(url)
        server = url.server
        id = url.id

    with PrivateBin(server) as client:
        client.delete(id=id, delete_token=delete_token)
