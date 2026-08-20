from __future__ import annotations

import re

import pytest

from privatebin import PrivateBin, PrivateBinServerError


def test_delete(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("delete me")
    pbin_client.delete(id=receipt.url.id, delete_token=receipt.delete_token)
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Document does not exist, has expired or has been deleted."),
    ):
        pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)


def test_delete_bad_token(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("delete me")
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Wrong deletion token. Document was not deleted."),
    ):
        pbin_client.delete(id=receipt.url.id, delete_token="invalidtoken")
