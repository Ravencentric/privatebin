from __future__ import annotations

import re

import pytest

from privatebin import PrivateBin


def test_create_invalid_feature() -> None:
    client = PrivateBin("https://example.com/")
    errmsg = (
        "Parameter 'feature' expected one of the following types: 'Feature', 'NoneType', "
        "but got 'str'."
    )
    with pytest.raises(TypeError, match=re.escape(errmsg)):
        client.create(text="hello world", feature="invalid")  # pyrefly: ignore[bad-argument-type]


def test_server_property() -> None:
    client = PrivateBin("https://example.com/")
    assert client.server == "https://example.com/"


@pytest.mark.parametrize(
    ("server", "expected"),
    [
        ("https://example.com", "https://example.com/"),
        ("https://example.com/", "https://example.com/"),
        ("https://example.com/privatebin", "https://example.com/privatebin/"),
        ("https://example.com/privatebin/", "https://example.com/privatebin/"),
        ("  https://example.com/  ", "https://example.com/"),
    ],
)
def test_server_normalization(server: str, expected: str) -> None:
    client = PrivateBin(server)
    assert client.server == expected


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
def test_server_invalid(server: str, reason: str) -> None:
    with pytest.raises(ValueError, match=re.escape(reason)):
        PrivateBin(server)


def test_context_manager() -> None:
    with PrivateBin("https://example.com/") as client:
        assert client.server == "https://example.com/"
