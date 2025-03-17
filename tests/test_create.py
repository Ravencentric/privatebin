from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from privatebin import Attachment, PrivateBin, PrivateBinError

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


def test_create(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={"status": 0, "id": "123456789", "url": "/?123456789", "deletetoken": "token"}
    )
    url = pbin_client.create("Hello World!")
    assert url.server == "https://privatebin.net/"
    assert url.id == "123456789"
    assert url.delete_token == "token"
    assert str(url) == "https://privatebin.net/?123456789#********"
    assert repr(url) == "https://privatebin.net/?123456789#********"


def test_create_with_attachment(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={"status": 0, "id": "123456789", "url": "/?123456789", "deletetoken": "token"}
    )
    attachment = Attachment(content=b"foo", name="bar.txt")
    url = pbin_client.create("Hello World!", attachment=attachment)
    assert url.server == "https://privatebin.net/"
    assert url.id == "123456789"
    assert url.delete_token == "token"
    assert str(url) == "https://privatebin.net/?123456789#********"
    assert repr(url) == "https://privatebin.net/?123456789#********"


def test_create_error(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "status": 1,
            "message": "Something went terribly wrong!",
        }
    )

    with pytest.raises(PrivateBinError, match="Something went terribly wrong!"):
        pbin_client.create(text="hello world")


def test_create_error_with_burn_and_open_discussion(pbin_client: PrivateBin) -> None:
    errmsg = (
        "Cannot create a paste with both 'burn_after_reading' and 'open_discussion' enabled. "
        "A paste that burns after reading cannot have open discussions."
    )

    with pytest.raises(PrivateBinError, match=errmsg):
        pbin_client.create(text="hello world", burn_after_reading=True, open_discussion=True)
