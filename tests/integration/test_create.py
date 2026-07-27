from __future__ import annotations

import pytest

from privatebin import Attachment, Formatter, PrivateBin, PrivateBinError


def test_create(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("Hello World!")
    assert receipt.url.server == pbin_client.server
    assert receipt.url.id
    assert receipt.delete_token
    assert str(receipt.url) == f"{pbin_client.server}?{receipt.url.id}#********"
    assert receipt.url.unmask() == f"{pbin_client.server}?{receipt.url.id}#{receipt.url.passphrase}"


def test_create_with_attachment(pbin_client: PrivateBin) -> None:
    attachment = Attachment(content=b"foo", name="bar.txt")
    receipt = pbin_client.create("Hello World!", attachment=attachment)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "Hello World!"
    assert paste.attachment is not None
    assert paste.attachment.name == "bar.txt"
    assert paste.attachment.content == b"foo"


def test_create_with_password(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("secret", password="hunter2")
    paste = pbin_client.get(
        id=receipt.url.id, passphrase=receipt.url.passphrase, password="hunter2"
    )
    assert paste.text == "secret"


def test_create_with_markdown(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("# Hello", formatter=Formatter.MARKDOWN)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "# Hello"
    assert paste.formatter is Formatter.MARKDOWN


def test_create_burn_after_reading(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("burn", burn_after_reading=True)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "burn"
    assert paste.burn_after_reading is True
    with pytest.raises(PrivateBinError):
        pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
