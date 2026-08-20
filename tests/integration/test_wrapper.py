from __future__ import annotations

import re

import pytest

import privatebin
from privatebin import PrivateBinServerError


def test_wrapper_create_get_roundtrip(server: str) -> None:
    receipt = privatebin.create("Hello World!", server=server)
    assert receipt.url.server == server
    paste = privatebin.get(receipt.url.unmask())
    assert paste.text == "Hello World!"


def test_wrapper_delete(server: str) -> None:
    receipt = privatebin.create("delete me", server=server)
    privatebin.delete(receipt.url.unmask(), delete_token=receipt.delete_token)

    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Document does not exist, has expired or has been deleted."),
    ):
        privatebin.get(receipt.url.unmask())
