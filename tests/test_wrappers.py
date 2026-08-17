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
            "Invalid PrivateBin URL: missing scheme or host. "
            "Expected '<server>/?<paste-id>#<passphrase>'. Got: 'whoops'."
        ),
    ):
        privatebin.get("whoops")


def test_wrapper_create_errors() -> None:
    with pytest.raises(TypeError, match="Parameter 'text' expected 'str', but got 'object'."):
        privatebin.create(
            object(),  # pyrefly: ignore[bad-argument-type]
            server="https://example.com/",
        )

    with pytest.raises(
        TypeError,
        match="Parameter 'server' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'NoneType'.",
    ):
        privatebin.create(
            "hello",
            server=None,  # pyrefly: ignore[bad-argument-type]
        )


def test_wrapper_delete_errors() -> None:
    with pytest.raises(
        TypeError,
        match="Parameter 'url' expected 'str', 'PrivateBinUrl', or 'PasteReceipt', but got 'object'.",
    ):
        privatebin.delete(
            url=object(),  # pyrefly: ignore[bad-argument-type]
            delete_token="hello",
        )
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid PrivateBin URL: missing scheme or host. "
            "Expected '<server>/?<paste-id>'. Got: 'whoops'."
        ),
    ):
        privatebin.delete("whoops", delete_token="hello")
