from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

import privatebin
from privatebin import PasteReceipt, PrivateBinUrl

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


@pytest.mark.parametrize(
    "url",
    (
        "https://bin.disroot.org/?8ed8eb3736994f7d#-5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        "https://privatebin.arch-linux.cz/?8ed8eb3736994f7d#-5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        PrivateBinUrl(
            server="https://privatebin.net/",
            id="8ed8eb3736994f7d",
            passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        ),
        PrivateBinUrl(
            server="https://0.0g.gg/",
            id="8ed8eb3736994f7d",
            passphrase="-5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        ),
    ),
    ids=repr,
)
def test_wrapper_get(url: str | PrivateBinUrl, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "status": 0,
            "id": "8ed8eb3736994f7d",
            "url": "/?8ed8eb3736994f7d=?8ed8eb3736994f7d",
            "adata": [
                [
                    "EhGlr6MDIrNHFyhdMAE6gA==",
                    "wATfGNcSqjM=",
                    100000,
                    256,
                    128,
                    "aes",
                    "gcm",
                    "zlib",
                ],
                "plaintext",
                0,
                0,
            ],
            "meta": {"time_to_live": 2591650},
            "v": 2,
            "ct": "NnMN8PGFNUzKNnXXz9DLhX/c5Ukb0rn61BDqZYVttkEqrUJDIm9r20bH",
            "comments": [],
            "comment_count": 0,
            "comment_offset": 0,
            "@context": "?jsonld=paste",
        }
    )

    paste = privatebin.get(url=url)
    assert paste.text == "Hello World!"


def test_wrapper_get_errors() -> None:
    with pytest.raises(
        TypeError,
        match="Parameter 'url' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'object'.",
    ):
        privatebin.get(object())  # type: ignore[arg-type]

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid PrivateBin URL format. URL should be like: https://examplebin.net/?pasteid#passphrase"
        ),
    ):
        privatebin.get("whoops")


@pytest.mark.parametrize(
    "server, expected",
    (
        ("https://privatebin.arch-linux.cz/", "https://privatebin.arch-linux.cz/"),
        (
            PrivateBinUrl(
                server="https://privatebin.net/",
                id="8ed8eb3736994f7d",
                passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
            ),
            "https://privatebin.net/",
        ),
        (
            PasteReceipt(
                url=PrivateBinUrl(
                    server="https://0.0g.gg/",
                    id="8ed8eb3736994f7d",
                    passphrase="-5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
                ),
                delete_token="blah",
            ),
            "https://0.0g.gg/",
        ),
    ),
    ids=repr,
)
def test_wrapper_create(server: str | PrivateBinUrl, expected: str, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={"status": 0, "id": "123456789", "url": "/?123456789", "deletetoken": "token"}
    )
    paste = privatebin.create("Hello World!", server=server)
    assert paste.url.id == "123456789"
    assert paste.url.server == expected
    assert paste.delete_token == "token"


def test_wrapper_create_errors() -> None:
    with pytest.raises(TypeError, match="Parameter 'text' expected 'str', but got 'object'."):
        privatebin.create(object())  # type: ignore[arg-type]

    with pytest.raises(
        TypeError,
        match="Parameter 'server' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'NoneType'.",
    ):
        privatebin.create("hello", server=None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "url",
    (
        "https://bin.disroot.org/?8ed8eb3736994f7d#-5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        "https://privatebin.arch-linux.cz/?8ed8eb3736994f7d",
        "https://privatebin.arch-linux.cz/?8ed8eb3736994f7d#",
        PrivateBinUrl(
            server="https://privatebin.net/",
            id="8ed8eb3736994f7d",
            passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        ),
        PasteReceipt(
            url=PrivateBinUrl(
                server="https://0.0g.gg/",
                id="8ed8eb3736994f7d",
                passphrase="-5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
            ),
            delete_token="blah",
        ),
    ),
    ids=repr,
)
def test_wrapper_delete(url: str | PrivateBinUrl, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"status": 0})
    privatebin.delete(url, delete_token="token")


def test_wrapper_delete_errors() -> None:
    with pytest.raises(
        TypeError,
        match="Parameter 'url' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'object'.",
    ):
        privatebin.delete(url=object(), delete_token="hello")  # type: ignore[arg-type]

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid PrivateBin URL format. URL should be like: https://examplebin.net/?pasteid"
        ),
    ):
        privatebin.delete("whoops", delete_token="hello")
