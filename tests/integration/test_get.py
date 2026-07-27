from __future__ import annotations

import pytest

from privatebin import Formatter, PrivateBin, PrivateBinError


def test_get(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("Hello World!")
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "Hello World!"
    assert paste.formatter is Formatter.PLAIN_TEXT
    assert paste.time_to_live is not None


def test_get_with_wrong_password(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("secret", password="correct")
    with pytest.raises(PrivateBinError):
        pbin_client.get(
            id=receipt.url.id,
            passphrase=receipt.url.passphrase,
            password="wrong",
        )


def test_get_with_wrong_passphrase(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("hello")
    with pytest.raises(PrivateBinError):
        pbin_client.get(
            id=receipt.url.id,
            passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        )


def test_get_nonexistent(pbin_client: PrivateBin) -> None:
    with pytest.raises(PrivateBinError):
        pbin_client.get(
            id="doesnotexist",
            passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        )
