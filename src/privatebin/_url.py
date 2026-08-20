from __future__ import annotations

from urllib.parse import urlsplit


def pb_urljoin(server: str, paste_id: str, passphrase: str | None = None) -> str:
    """
    Build a PrivateBin URL string with the given passphrase at the end.

    The stdlib `urllib.parse.urljoin` is not suitable for this. Joining
    `/?id#key` onto the server URL makes the leading slash replace the
    server's path instead of keeping it, breaking instances hosted in a
    subdirectory like `https://example.com/privatebin/`. Joining it without
    the slash appends the `?` straight onto the path when the server URL
    has no trailing slash. A `None` passphrase omits the fragment.
    """
    base = f"{server.rstrip('/')}/?{paste_id}"
    return base if not passphrase else f"{base}#{passphrase}"


def pb_urlsplit(url: str, /) -> tuple[str, str, str | None]:
    """
    Parse a PrivateBin URL string into its `(server, id, passphrase)` parts.

    The `server` is returned exactly as given, including any subdirectory
    path and trailing slash. The `passphrase` is `None` when the URL has no
    fragment, or when the fragment is empty (`https://example.com/?id#`).
    A leading hyphen (the visual cue for burn-after-reading pastes) is
    stripped from the passphrase.
    """
    server, has_query, id_and_passphrase = url.strip().partition("?")

    parsed = urlsplit(server)
    if not (parsed.scheme and parsed.netloc):
        msg = "missing scheme or host"
        raise ValueError(msg)

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
