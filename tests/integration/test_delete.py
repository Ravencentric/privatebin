from __future__ import annotations

import re

import pytest

from privatebin import PrivateBin, PrivateBinServerError


def test_delete(pb: PrivateBin) -> None:
    receipt = pb.create("delete me")
    pb.delete(id=receipt.url.id, delete_token=receipt.delete_token)
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Document does not exist, has expired or has been deleted."),
    ):
        pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)


def test_delete_bad_token(pb: PrivateBin) -> None:
    receipt = pb.create("delete me")
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Wrong deletion token. Document was not deleted."),
    ):
        pb.delete(id=receipt.url.id, delete_token="invalidtoken")
