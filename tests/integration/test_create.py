from __future__ import annotations

import pytest

from privatebin import (
    Attachment,
    Compression,
    Expiration,
    Formatter,
    Mode,
    PrivateBin,
    PrivateBinError,
)


def test_create(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("Hello World!")
    assert receipt.url.server == pbin_client.server
    assert receipt.url.id
    assert receipt.delete_token
    assert str(receipt.url) == f"{pbin_client.server}?{receipt.url.id}#********"
    assert (
        receipt.url.unmask() == f"{pbin_client.server}?{receipt.url.id}#{receipt.url.passphrase}"
    )


def test_create_with_attachment(pbin_client: PrivateBin) -> None:
    attachment = Attachment(content=b"foo", name="bar.txt")
    receipt = pbin_client.create("Hello World!", attachments=attachment)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "Hello World!"
    assert len(paste.attachments) == 1
    assert paste.attachments[0].name == "bar.txt"
    assert paste.attachments[0].content == b"foo"


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


def test_create_with_source_code(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("print('hello')", formatter=Formatter.SOURCE_CODE)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "print('hello')"
    assert paste.formatter is Formatter.SOURCE_CODE


def test_create_with_no_compression(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("hello", compression=Compression.NONE)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "hello"


def test_create_with_open_discussion(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("discuss", mode=Mode.OPEN_DISCUSSION)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "discuss"
    assert paste.mode is Mode.OPEN_DISCUSSION


def test_create_never_expires(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("forever", expiration=Expiration.NEVER)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "forever"
    assert paste.time_to_live is None


def test_create_burn_after_reading(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("burn", mode=Mode.BURN_AFTER_READING)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "burn"
    assert paste.mode is Mode.BURN_AFTER_READING
    with pytest.raises(PrivateBinError):
        pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)


def test_create_burn_after_reading_with_password(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create("burn secret", mode=Mode.BURN_AFTER_READING, password="hunter2")
    paste = pbin_client.get(
        id=receipt.url.id,
        passphrase=receipt.url.passphrase,
        password="hunter2",
    )
    assert paste.text == "burn secret"
    assert paste.mode is Mode.BURN_AFTER_READING
    with pytest.raises(PrivateBinError):
        pbin_client.get(
            id=receipt.url.id,
            passphrase=receipt.url.passphrase,
            password="hunter2",
        )


def test_create_burn_after_reading_with_attachment(pbin_client: PrivateBin) -> None:
    attachment = Attachment(content=b"burn", name="burn.txt")
    receipt = pbin_client.create("burn text", mode=Mode.BURN_AFTER_READING, attachments=attachment)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "burn text"
    assert len(paste.attachments) == 1
    assert paste.attachments[0].content == b"burn"
    assert paste.mode is Mode.BURN_AFTER_READING


def test_create_burn_after_reading_with_markdown(pbin_client: PrivateBin) -> None:
    receipt = pbin_client.create(
        "# burn", mode=Mode.BURN_AFTER_READING, formatter=Formatter.MARKDOWN
    )
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "# burn"
    assert paste.formatter is Formatter.MARKDOWN
    assert paste.mode is Mode.BURN_AFTER_READING


def test_create_with_multiple_attachments(pbin_client: PrivateBin) -> None:
    attachments = (
        Attachment(content=b"foo", name="foo.txt"),
        Attachment(content=b"bar", name="bar.txt"),
    )
    receipt = pbin_client.create("multiple attachments", attachments=attachments)
    paste = pbin_client.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "multiple attachments"
    assert len(paste.attachments) == 2
    assert paste.attachments[0].name == "foo.txt"
    assert paste.attachments[0].content == b"foo"
    assert paste.attachments[1].name == "bar.txt"
    assert paste.attachments[1].content == b"bar"
