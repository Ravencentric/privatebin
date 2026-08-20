from __future__ import annotations

import re

import pytest

from privatebin import (
    Formatter,
    PrivateBin,
    PrivateBinDecryptionError,
    PrivateBinServerError,
)


def test_get(pb: PrivateBin) -> None:
    receipt = pb.create("Hello World!")
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "Hello World!"
    assert paste.formatter is Formatter.PLAIN_TEXT
    assert paste.time_to_live is not None


def test_get_with_wrong_password(pb: PrivateBin) -> None:
    receipt = pb.create("secret", password="correct")
    with pytest.raises(
        PrivateBinDecryptionError,
        match=re.escape("Failed to decrypt paste. Check the passphrase and password."),
    ):
        pb.get(
            id=receipt.url.id,
            passphrase=receipt.url.passphrase,
            password="wrong",
        )


def test_get_with_wrong_passphrase(pb: PrivateBin) -> None:
    receipt = pb.create("hello")
    with pytest.raises(
        PrivateBinDecryptionError,
        match=re.escape("Failed to decrypt paste. Check the passphrase and password."),
    ):
        pb.get(
            id=receipt.url.id,
            passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        )


def test_get_nonexistent(pb: PrivateBin) -> None:
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Invalid document ID."),
    ):
        pb.get(
            id="doesnotexist",
            passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        )
