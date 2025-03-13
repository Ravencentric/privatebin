from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from privatebin import Formatter, PrivateBin, PrivateBinError

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


def test_get(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
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

    paste = pbin_client.get(
        id="8ed8eb3736994f7d", passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH"
    )
    assert paste.text == "Hello World!"


def test_get_with_password(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "status": 0,
            "id": "fca0ed97b16b4fbc",
            "url": "/?fca0ed97b16b4fbc?fca0ed97b16b4fbc",
            "adata": [
                [
                    "AFwXgqZ86FAEV1/bGUariw==",
                    "yNy9SmT13zE=",
                    100000,
                    256,
                    128,
                    "aes",
                    "gcm",
                    "zlib",
                ],
                "markdown",
                0,
                0,
            ],
            "meta": {"time_to_live": 69655},
            "v": 2,
            "ct": "ig3kAeunDjTOOmXRsmCxTpxbeXNMfyjk8ABkkDs+YdrDVHZBByn9kNgFAT3lUbp0v3kxrOcAXXLW8yl80qkbqg==",
            "comments": [],
            "comment_count": 0,
            "comment_offset": 0,
            "@context": "?jsonld=paste",
        }
    )

    paste = pbin_client.get(
        id="fca0ed97b16b4fbc",
        passphrase="9Hv9454VREzvP5XPRZGkwe7snFGJwQ8yj6yqkwU8JAMX",
        password="8G$SMW@rpE",
    )
    assert paste.text == "# Hello from password protected paste!"
    assert paste.formatter is Formatter.MARKDOWN


def test_get_with_attachment(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "status": 0,
            "id": "ba0f3d1b841cc9b0",
            "url": "/?ba0f3d1b841cc9b0=?ba0f3d1b841cc9b0",
            "adata": [
                [
                    "UBTftZ+Qc5u6B39/Q/3N6A==",
                    "FmAX6Dhuz3U=",
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
            "meta": {"time_to_live": 86169},
            "v": 2,
            "ct": "JZS+rANCtgGVt8+40tNtK3Pl4w1IR8MdcuZ+7OY/esQXMdN6nsX2vuvhICFFf/mPF6UzG3t59RCpWuhoJktXY4Bv0wDzajZGJOBBBBT6Ysn7wer5Wn5VExhrWqZKHiwDPZrzWiRn2pTRmCWDJw==",
            "comments": [],
            "comment_count": 0,
            "comment_offset": 0,
            "@context": "?jsonld=paste",
        }
    )

    paste = pbin_client.get(
        id="ba0f3d1b841cc9b0", passphrase="vHvco9qjB628q3pc49ajft3tANoxmeMp5ePomi4VagR"
    )
    assert paste.text == "Hello Attachments!"
    assert paste.attachment is not None
    assert paste.attachment.name == "attachment.txt"
    assert paste.attachment.content == b"Hello World!"


def test_get_error(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "status": 1,
            "message": "Something went terribly wrong!",
        }
    )

    with pytest.raises(PrivateBinError, match="Something went terribly wrong!"):
        pbin_client.get(
            id="8ed8eb3736994f7d", passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH"
        )


def test_get_unsupported_api_version_1(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"status": 0, "v": 1})

    with pytest.raises(
        PrivateBinError,
        match=re.escape("Only the v2 API is supported (PrivateBin >= 1.3). Got API version: 1"),
    ):
        pbin_client.get(
            id="8ed8eb3736994f7d", passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH"
        )


def test_get_unsupported_api_version_2(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"status": 0, "v": 3})

    with pytest.raises(
        PrivateBinError,
        match=re.escape("Only the v2 API is supported (PrivateBin >= 1.3). Got API version: 3"),
    ):
        pbin_client.get(
            id="8ed8eb3736994f7d", passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH"
        )
