from __future__ import annotations

import re

import pytest

from privatebin import PrivateBin, PrivateBinError
from privatebin._models import PasteJsonLD


def test_create_burn_after_reading_and_open_discussion() -> None:
    client = PrivateBin("https://example.com/")
    errmsg = (
        "Cannot create a paste with both 'burn_after_reading' and 'open_discussion' enabled. "
        "A paste that burns after reading cannot have open discussions."
    )
    with pytest.raises(PrivateBinError, match=errmsg):
        client.create(text="hello world", burn_after_reading=True, open_discussion=True)


@pytest.mark.parametrize("version", [1, 3])
def test_unsupported_api_version(version: int) -> None:
    response: dict[str, object] = {"status": 0, "v": version}
    with pytest.raises(
        PrivateBinError,
        match=re.escape(
            f"Only the v2 API is supported (PrivateBin >= 1.3). Got API version: {version}"
        ),
    ):
        PasteJsonLD.from_response(response)


def test_get_error_response() -> None:
    with pytest.raises(PrivateBinError, match="Something went terribly wrong!"):
        PasteJsonLD.from_response({"status": 1, "message": "Something went terribly wrong!"})


def test_server_property() -> None:
    client = PrivateBin("https://example.com/")
    assert client.server == "https://example.com/"


def test_context_manager() -> None:
    with PrivateBin("https://example.com/") as client:
        assert client.server == "https://example.com/"
