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


def test_context_manager() -> None:
    with PrivateBin("https://example.com/") as client:
        assert client.server == "https://example.com/"
