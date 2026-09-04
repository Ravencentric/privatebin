from __future__ import annotations

from urllib.parse import urlsplit


def pb_normalize_server_url(server: str, /) -> str:
    """
    Validate and normalize a PrivateBin server URL.

    The server must have a scheme and host and must not contain a query
    string or fragment. The returned URL preserves any subdirectory path
    and has exactly one trailing slash.
    """
    server = server.strip()
    parsed = urlsplit(server)

    if not (parsed.scheme and parsed.netloc):
        msg = "missing scheme or host"
        raise ValueError(msg)

    if parsed.query or parsed.fragment or "?" in server or "#" in server:
        # The raw-string checks are load-bearing: urlsplit() reports an empty
        # query/fragment as "" (falsy), so without them inputs like
        # "https://example.com/?" or "https://example.com/#" would slip
        # through and normalize to a broken ".../?/" URL.
        msg = "server URL must not contain a query or fragment"
        raise ValueError(msg)

    return server.rstrip("/") + "/"


def pb_urljoin(server: str, paste_id: str, passphrase: str | None = None) -> str:
    """
    Build a PrivateBin URL string with the given passphrase at the end.
    A `None` passphrase omits the fragment.

    The stdlib `urllib.parse.urljoin` is not suitable for this. Joining
    `/?id#key` onto the server URL makes the leading slash replace the
    server's path instead of keeping it, breaking instances hosted in a
    subdirectory like `https://example.com/privatebin/`. Joining it without
    the slash appends the `?` straight onto the path when the server URL
    has no trailing slash.
    """
    server = pb_normalize_server_url(server)
    base = f"{server}?{paste_id}"
    return base if not passphrase else f"{base}#{passphrase}"


def pb_urlsplit(url: str, /) -> tuple[str, str, str | None]:
    """
    Parse a PrivateBin URL string into its `(server, id, passphrase)` parts.
    Note that this also performs normalization.

    The `passphrase` is `None` when the URL has no fragment, or when the
    fragment is empty (`https://example.com/?id#`). A leading hyphen (the
    visual cue for burn-after-reading pastes) is stripped from the passphrase.
    """
    server, has_query, id_and_passphrase = url.strip().partition("?")
    server = pb_normalize_server_url(server)

    if not has_query:
        msg = "missing '?<paste-id>' component"
        raise ValueError(msg)

    id, has_fragment, passphrase = id_and_passphrase.partition("#")

    if not id:
        msg = "empty paste ID"
        raise ValueError(msg)

    if has_fragment:
        # The leading hyphen is a visual cue for "burn-after-reading" pastes.
        # This code removes it because it's not part of the actual passphrase
        # and would cause decryption to fail. Removing it also ensures that
        # pastes with and without the hyphen are treated as identical.
        passphrase = passphrase.removeprefix("-")

    return server, id, passphrase if passphrase else None
