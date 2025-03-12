from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from privatebin import PrivateBin, PrivateBinError


def test_delete(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"status": 0, "id": "123456789"})
    pbin_client.delete(id="123456789", delete_token="token")


def test_delete_error(pbin_client: PrivateBin, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "status": 1,
            "message": "Something went terribly wrong!",
        }
    )

    with pytest.raises(PrivateBinError, match="Something went terribly wrong!"):
        pbin_client.delete(id="123456789", delete_token="token")
