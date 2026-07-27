from __future__ import annotations

import pytest

from privatebin import Formatter, PrivateBin, PrivateBinError


def test_get(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("Hello World!")
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "Hello World!"
    assert paste.formatter is Formatter.PLAIN_TEXT
    assert paste.time_to_live is not None


def test_get_nonexistent(pbin_client: PrivateBin) -> None:
    with pytest.raises(PrivateBinError):
        pbin_client.get(
            id="doesnotexist",
            passphrase="5qLFA8Vueqg5g7dAXZ3FLZBL6JQpzSwXzjwJahVsUFbH",
        )
