from __future__ import annotations

import re

import pytest

from privatebin._url import pb_normalize_server_url, pb_urljoin, pb_urlsplit


@pytest.mark.parametrize(
    ("server", "expected"),
    [
        ("https://example.com", "https://example.com/"),
        ("https://example.com/", "https://example.com/"),
        ("https://example.com/privatebin", "https://example.com/privatebin/"),
        ("https://example.com/privatebin/", "https://example.com/privatebin/"),
        ("  https://example.com/  ", "https://example.com/"),
        ("  https://example.com/privatebin  ", "https://example.com/privatebin/"),
        ("https://example.com///", "https://example.com/"),
    ],
)
def test_pb_normalize_server_url(server: str, expected: str) -> None:
    assert pb_normalize_server_url(server) == expected


@pytest.mark.parametrize(
    ("server", "reason"),
    [
        ("whoops", "missing scheme or host"),
        ("", "missing scheme or host"),
        ("a?b#c", "missing scheme or host"),
        ("https://example.com/?", "server URL must not contain a query or fragment"),
        ("https://example.com/#", "server URL must not contain a query or fragment"),
        (
            "https://example.com/?pasteid",
            "server URL must not contain a query or fragment",
        ),
        (
            "https://example.com/#fragment",
            "server URL must not contain a query or fragment",
        ),
        (
            "https://example.com/privatebin?pasteid",
            "server URL must not contain a query or fragment",
        ),
    ],
)
def test_pb_normalize_server_url_errors(server: str, reason: str) -> None:
    with pytest.raises(ValueError, match=re.escape(reason)):
        pb_normalize_server_url(server)


@pytest.mark.parametrize(
    ("server", "paste_id", "passphrase", "expected"),
    [
        ("https://example.com/", "pasteid", "secret", "https://example.com/?pasteid#secret"),
        (
            "https://example.com/privatebin/",
            "pasteid",
            "secret",
            "https://example.com/privatebin/?pasteid#secret",
        ),
        (
            "https://example.com/privatebin",
            "pasteid",
            "secret",
            "https://example.com/privatebin/?pasteid#secret",
        ),
        ("https://example.com/", "pasteid", "", "https://example.com/?pasteid"),
        ("https://example.com/", "pasteid", None, "https://example.com/?pasteid"),
    ],
)
def test_pb_urljoin(server: str, paste_id: str, passphrase: str | None, expected: str) -> None:
    assert pb_urljoin(server, paste_id, passphrase) == expected


@pytest.mark.parametrize(
    ("server", "reason"),
    [
        ("whoops", "missing scheme or host"),
        (
            "https://example.com/?pasteid",
            "server URL must not contain a query or fragment",
        ),
        (
            "https://example.com/#fragment",
            "server URL must not contain a query or fragment",
        ),
    ],
)
def test_pb_urljoin_invalid_server(server: str, reason: str) -> None:
    with pytest.raises(ValueError, match=re.escape(reason)):
        pb_urljoin(server, "pasteid", "secret")


@pytest.mark.parametrize(
    ("server", "id", "expected"),
    [
        (
            "https://example.com/",
            "pasteid",
            "https://example.com/?pasteid",
        ),
        (
            "https://example.com/privatebin",
            "pasteid",
            "https://example.com/privatebin/?pasteid",
        ),
        (
            "https://example.com/privatebin/",
            "pasteid",
            "https://example.com/privatebin/?pasteid",
        ),
    ],
)
def test_pb_urljoin_default_passphrase(server: str, id: str, expected: str) -> None:
    assert pb_urljoin(server, id) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://privatebin.net/?926bdda997f89847#7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb",
            "https://privatebin.net/?926bdda997f89847#7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb",
        ),
        (
            "https://example.com/privatebin/?pasteid#secret",
            "https://example.com/privatebin/?pasteid#secret",
        ),
        (
            "https://example.com/privatebin/?pasteid",
            "https://example.com/privatebin/?pasteid",
        ),
        ("https://example.com/?pasteid", "https://example.com/?pasteid"),
        ("https://example.com/?pasteid#", "https://example.com/?pasteid"),
        ("https://example.com/?pasteid#-secret", "https://example.com/?pasteid#secret"),
        ("  https://example.com/?pasteid#secret  ", "https://example.com/?pasteid#secret"),
        ("https://example.com/privatebin?pasteid", "https://example.com/privatebin/?pasteid"),
    ],
)
def test_pb_urlsplit_roundtrip(url: str, expected: str) -> None:
    server, id, passphrase = pb_urlsplit(url)
    assert pb_urljoin(server, id, passphrase) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://privatebin.net/?926bdda997f89847#7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb",
            (
                "https://privatebin.net/",
                "926bdda997f89847",
                "7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb",
            ),
        ),
        (
            "https://example.com/privatebin/?pasteid#secret",
            ("https://example.com/privatebin/", "pasteid", "secret"),
        ),
        (
            "https://example.com/privatebin?pasteid",
            ("https://example.com/privatebin/", "pasteid", None),
        ),
        ("https://example.com/?pasteid", ("https://example.com/", "pasteid", None)),
        ("https://example.com/?pasteid#", ("https://example.com/", "pasteid", None)),
        (
            "https://example.com/?pasteid#-secret",
            ("https://example.com/", "pasteid", "secret"),
        ),
        (
            "  https://example.com/?pasteid#secret  ",
            ("https://example.com/", "pasteid", "secret"),
        ),
    ],
)
def test_pb_urlsplit(url: str, expected: tuple[str, str, str | None]) -> None:
    assert pb_urlsplit(url) == expected


@pytest.mark.parametrize(
    ("url", "reason"),
    [
        ("whoops", "missing scheme or host"),
        ("https://example.com", "missing '?<paste-id>' component"),
        ("a?b#c", "missing scheme or host"),
        ("https://example.com/?", "empty paste ID"),
        ("https://example.com/?#pasteid", "empty paste ID"),
    ],
)
def test_pb_urlsplit_errors(url: str, reason: str) -> None:
    with pytest.raises(ValueError, match=re.escape(reason)):
        pb_urlsplit(url)
