from __future__ import annotations

import re

import pytest

from privatebin import (
    Attachment,
    Compression,
    Expiration,
    Feature,
    Formatter,
    PrivateBin,
    PrivateBinServerError,
)


def test_create(pb: PrivateBin) -> None:
    receipt = pb.create("Hello World!")
    assert receipt.url.server == pb.server
    assert receipt.url.id
    assert receipt.delete_token
    assert str(receipt.url) == f"{pb.server}?{receipt.url.id}#********"
    assert receipt.url.unmask() == f"{pb.server}?{receipt.url.id}#{receipt.url.passphrase}"


def test_create_with_attachment(pb: PrivateBin) -> None:
    attachment = Attachment(content=b"foo", name="bar.txt")
    receipt = pb.create("Hello World!", attachments=attachment)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "Hello World!"
    assert len(paste.attachments) == 1
    assert paste.attachments[0].name == "bar.txt"
    assert paste.attachments[0].content == b"foo"


def test_create_with_password(pb: PrivateBin) -> None:
    receipt = pb.create("secret", password="hunter2")
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase, password="hunter2")
    assert paste.text == "secret"


def test_create_with_markdown(pb: PrivateBin) -> None:
    receipt = pb.create("# Hello", formatter=Formatter.MARKDOWN)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "# Hello"
    assert paste.formatter is Formatter.MARKDOWN


def test_create_with_source_code(pb: PrivateBin) -> None:
    receipt = pb.create("print('hello')", formatter=Formatter.SOURCE_CODE)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "print('hello')"
    assert paste.formatter is Formatter.SOURCE_CODE


def test_create_with_no_compression(pb: PrivateBin) -> None:
    receipt = pb.create("hello", compression=Compression.NONE)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "hello"


def test_create_with_open_discussion(pb: PrivateBin) -> None:
    receipt = pb.create("discuss", feature=Feature.OPEN_DISCUSSION)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "discuss"
    assert paste.feature is Feature.OPEN_DISCUSSION


def test_create_never_expires(pb: PrivateBin) -> None:
    receipt = pb.create("forever", expiration=Expiration.NEVER)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "forever"
    assert paste.time_to_live is None


def test_create_burn_after_reading(pb: PrivateBin) -> None:
    receipt = pb.create("burn", feature=Feature.BURN_AFTER_READING)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "burn"
    assert paste.feature is Feature.BURN_AFTER_READING
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Document does not exist, has expired or has been deleted."),
    ):
        pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)


def test_create_burn_after_reading_with_password(pb: PrivateBin) -> None:
    receipt = pb.create("burn secret", feature=Feature.BURN_AFTER_READING, password="hunter2")
    paste = pb.get(
        id=receipt.url.id,
        passphrase=receipt.url.passphrase,
        password="hunter2",
    )
    assert paste.text == "burn secret"
    assert paste.feature is Feature.BURN_AFTER_READING
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape("Document does not exist, has expired or has been deleted."),
    ):
        pb.get(
            id=receipt.url.id,
            passphrase=receipt.url.passphrase,
            password="hunter2",
        )


def test_create_burn_after_reading_with_attachment(pb: PrivateBin) -> None:
    attachment = Attachment(content=b"burn", name="burn.txt")
    receipt = pb.create("burn text", feature=Feature.BURN_AFTER_READING, attachments=attachment)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "burn text"
    assert len(paste.attachments) == 1
    assert paste.attachments[0].content == b"burn"
    assert paste.feature is Feature.BURN_AFTER_READING


def test_create_burn_after_reading_with_markdown(pb: PrivateBin) -> None:
    receipt = pb.create("# burn", feature=Feature.BURN_AFTER_READING, formatter=Formatter.MARKDOWN)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "# burn"
    assert paste.formatter is Formatter.MARKDOWN
    assert paste.feature is Feature.BURN_AFTER_READING


def test_create_with_multiple_attachments(pb: PrivateBin) -> None:
    attachments = (
        Attachment(content=b"foo", name="foo.txt"),
        Attachment(content=b"bar", name="bar.txt"),
    )
    receipt = pb.create("multiple attachments", attachments=attachments)
    paste = pb.get(id=receipt.url.id, passphrase=receipt.url.passphrase)
    assert paste.text == "multiple attachments"
    assert len(paste.attachments) == 2
    assert paste.attachments[0].name == "foo.txt"
    assert paste.attachments[0].content == b"foo"
    assert paste.attachments[1].name == "bar.txt"
    assert paste.attachments[1].content == b"bar"
