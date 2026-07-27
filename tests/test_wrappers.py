from __future__ import annotations

import re

import pytest

import privatebin


def test_wrapper_get_errors() -> None:
    with pytest.raises(
        TypeError,
        match="Parameter 'url' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'object'.",
    ):
        privatebin.get(object())  # pyrefly: ignore[bad-argument-type]

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid PrivateBin URL format. URL should be like: https://examplebin.net/?pasteid#passphrase"
        ),
    ):
        privatebin.get("whoops")


def test_wrapper_create_errors() -> None:
    with pytest.raises(TypeError, match="Parameter 'text' expected 'str', but got 'object'."):
        privatebin.create(object())  # pyrefly: ignore[bad-argument-type]

    with pytest.raises(
        TypeError,
        match="Parameter 'server' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'NoneType'.",
    ):
        privatebin.create("hello", server=None)  # pyrefly: ignore[bad-argument-type]


def test_wrapper_delete_errors() -> None:
    with pytest.raises(
        TypeError,
        match="Parameter 'url' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'object'.",
    ):
        privatebin.delete(url=object(), delete_token="hello")  # pyrefly: ignore[bad-argument-type]

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid PrivateBin URL format. URL should be like: https://examplebin.net/?pasteid"
        ),
    ):
        privatebin.delete("whoops", delete_token="hello")
