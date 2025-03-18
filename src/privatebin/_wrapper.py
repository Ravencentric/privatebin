from __future__ import annotations

from privatebin._core import PrivateBin
from privatebin._enums import Compression, Expiration, Formatter
from privatebin._models import Attachment, Paste, PrivateBinUrl


def get(url: str | PrivateBinUrl, *, password: str | None = None) -> Paste:
    """
    Retrieve and decrypt a paste from a PrivateBin URL.

    Parameters
    ----------
    url : str | PrivateBinUrl
        The complete URL of the PrivateBin paste.
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
        If the provided URL string is not in the expected format.
    TypeError
        If the provided `url` is not a string or a `PrivateBinUrl` object.

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

    paste = privatebin.get("https://privatebin.net/?pasteid#passphrase", password="pastepassword")
    print(paste.text)
    ```

    """
    match url:
        case str():
            # https://privatebin.net/?926bdda997f89847#7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb
            # https://bin.disroot.org/?4d7bc697fdea1c28#-DG2Snjk96vLtzPHLgtidHzAyL1pzKY6fru8KrsUY7Nzj
            # https://0.0g.gg/?2f03f0f4297cc91e#Ek1V4dtDpgjB2xngv6Wz5m1iMGNoB6EvRswcEEjMUFMk
            # https://privatebin.arch-linux.cz/?f73477514b655dbf#-A751k9CWbR5Y5UiYb7VmK2x5HwXqETABXoCTYuPt9t9a
            try:
                server, idpass = url.split("?")
                id, passphrase = idpass.split("#")
            except ValueError:
                msg = "Invalid PrivateBin URL format. URL should be like: https://examplebin.net/?pasteid#passphrase"
                raise ValueError(msg) from None
        case PrivateBinUrl():
            server = url.server
            id = url.id
            passphrase = url.passphrase
        case _:
            msg = f"Expected str or PrivateBinUrl, got {type(url).__name__}."
            raise TypeError(msg)

    with PrivateBin(server) as client:
        return client.get(id=id, passphrase=passphrase, password=password)


def create(  # noqa: PLR0913
    text: str,
    *,
    server: str | PrivateBinUrl = "https://privatebin.net/",
    attachment: Attachment | None = None,
    password: str | None = None,
    burn_after_reading: bool = False,
    open_discussion: bool = False,
    expiration: Expiration = Expiration.ONE_WEEK,
    formatter: Formatter = Formatter.PLAIN_TEXT,
    compression: Compression = Compression.ZLIB,
) -> PrivateBinUrl:
    """
    Create a new paste on PrivateBin.

    Parameters
    ----------
    text : str
        The text content of the paste.
    server : str | PrivateBinUrl, optional
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
    PrivateBinUrl
        A `PrivateBinUrl` object containing the URL to access the newly created paste,
        including the decryption passphrase and delete token.

    Raises
    ------
    PrivateBinError
        - If `burn_after_reading` and `open_discussion` are both set to `True`.
        - If there is an error during paste creation on PrivateBin.
    TypeError
        If the provided `url` is not a string or a `PrivateBinUrl` object.

    Examples
    --------
    Create a simple paste on the default PrivateBin instance:

    ```python
    paste_url = privatebin.create("Hello, PrivateBin!")
    print(f"Paste URL: {paste_url}")
    ```

    Create a paste on a custom PrivateBin server with Markdown formatting and burn-after-reading:

    ```python
    import privatebin
    from privatebin import Formatter

    md_paste_url = privatebin.create(
        text="# Markdown Content\\n\\nThis is **markdown** formatted text.",
        server="https://myprivatebin.example.org/",
        formatter=Formatter.MARKDOWN,
        burn_after_reading=True
    )
    print(f"Markdown paste URL: {md_paste_url}")
    ```

    Create a password-protected paste with an attachment:

    ```python
    import privatebin
    from privatebin import Attachment

    attachment = Attachment.from_file("path/to/your/file.txt")

    password_paste_url = privatebin.create(
        text="This paste has a password and an attachment.",
        password="supersecret",
        attachment=attachment
    )

    print(f"Password-protected paste URL: {password_paste_url}")
    ```

    """
    match server:
        case str():
            _server = server
        case PrivateBinUrl():
            _server = server.server
        case _:
            msg = f"Parameter 'server' expected str or PrivateBinUrl, got {type(server).__name__}."
            raise TypeError(msg)

    if not isinstance(text, str):
        msg = f"Parameter 'text' expected str, got {type(text).__name__}."
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


def delete(url: str | PrivateBinUrl, *, delete_token: str) -> None:
    """
    Delete a paste from PrivateBin using its URL and delete token.

    Parameters
    ----------
    url : str | PrivateBinUrl
        The complete URL of the PrivateBin paste, with or without the passphrase.
    delete_token : str
        The delete token associated with the paste.

    Raises
    ------
    PrivateBinError
        If there is an error deleting the paste on PrivateBin.
    ValueError
        If the provided URL string is not in the expected format.
    TypeError
        If the provided `url` is not a string or a `PrivateBinUrl` object.

    Examples
    --------
    ```python
    import privatebin

    paste_url = privatebin.create(text="This paste will be deleted.")
    delete(paste_url, delete_token=paste_url.delete_token)
    print(f"Paste with URL '{delete_url}' deleted.")
    ```

    """
    match url:
        case str():
            # https://privatebin.net/?926bdda997f89847#7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb
            # https://bin.disroot.org/?4d7bc697fdea1c28#-DG2Snjk96vLtzPHLgtidHzAyL1pzKY6fru8KrsUY7Nzj
            # https://0.0g.gg/?2f03f0f4297cc91e#Ek1V4dtDpgjB2xngv6Wz5m1iMGNoB6EvRswcEEjMUFMk
            # https://privatebin.arch-linux.cz/?f73477514b655dbf#-A751k9CWbR5Y5UiYb7VmK2x5HwXqETABXoCTYuPt9t9a
            try:
                server, idpass = url.split("?")
                id = idpass.split("#")[0]
            except (ValueError, KeyError):
                msg = "Invalid PrivateBin URL format. URL should be like: https://examplebin.net/?pasteid#passphrase"
                raise ValueError(msg) from None
        case PrivateBinUrl():
            server = url.server
            id = url.id
        case _:
            msg = f"Expected str or PrivateBinUrl, got {type(url).__name__}."
            raise TypeError(msg)

    with PrivateBin(server) as client:
        client.delete(id=id, delete_token=delete_token)
