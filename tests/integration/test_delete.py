from __future__ import annotations

import pytest

from privatebin import PrivateBin, PrivateBinError


def test_delete(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("delete me")
    pbin_client.delete(id=receipt.url.id, delete_token=receipt.delete_token)
    with pytest.raises(PrivateBinError):
        pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)


def test_delete_bad_token(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("delete me")
    with pytest.raises(PrivateBinError):
        pbin_client.delete(id=receipt.url.id, delete_token="invalidtoken")
