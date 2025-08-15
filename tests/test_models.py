from __future__ import annotations

import base64
import re
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from privatebin import Attachment, Formatter, Paste, PrivateBinUrl

if TYPE_CHECKING:
    from pathlib import Path


def test_attachment_from_file(tmp_path: Path) -> None:
    file = tmp_path / "attachment.txt"
    file.write_bytes(b"hello from attachment")

    attachment = Attachment.from_file(file)
    assert attachment.name == "attachment.txt"
    assert attachment.content == b"hello from attachment"

    assert attachment.to_data_url() == "data:text/plain;base64,aGVsbG8gZnJvbSBhdHRhY2htZW50"
    assert attachment == Attachment.from_data_url(
        url="data:text/plain;base64,aGVsbG8gZnJvbSBhdHRhY2htZW50", name="attachment.txt"
    )
    assert Attachment.from_json(attachment.to_json()) == attachment


def test_attachment_from_file_with_different_name(tmp_path: Path) -> None:
    file = tmp_path / "attachment.txt"
    file.write_bytes(b"hello from attachment")

    attachment = Attachment.from_file(file, name="hello.txt")
    assert attachment.name == "hello.txt"
    assert attachment.content == b"hello from attachment"

    assert attachment.to_data_url() == "data:text/plain;base64,aGVsbG8gZnJvbSBhdHRhY2htZW50"


def test_attachment_from_file_error(tmp_path: Path) -> None:
    file = tmp_path / "attachment.txt"

    with pytest.raises(FileNotFoundError, match=re.escape(str(file))):
        Attachment.from_file(file)


def test_attachment_from_b64() -> None:
    original = b"Foo and bar"
    data = base64.b64encode(original).decode()

    attachment = Attachment.from_data_url(
        url=f"data:application/octet-stream;base64,{data}", name="baz"
    )
    assert attachment.name == "baz"
    assert attachment.content == b"Foo and bar"

    assert attachment.to_data_url() == "data:application/octet-stream;base64,Rm9vIGFuZCBiYXI="


def test_attachment_from_b64_error() -> None:
    original = b"Foo and bar"
    data = base64.b64encode(original).decode()
    url = f"data:application/octet-stream;base65,{data}"

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Paste has an invalid or unsupported attachment. "
            "Expected a data URL: 'data:<mimetype>;base64,<data>', got: 'data:application/octet-stream;base65,Rm9vIGFuZCBiY... (TRUNCATED)'"
        ),
    ):
        Attachment.from_data_url(url=url, name="baz.txt")


def test_paste_json_roundtrip() -> None:
    paste = Paste(
        id="abcdef",
        text="hello world",
        attachment=Attachment(name="baz.txt", content=b"Foo and bar"),
        formatter=Formatter.MARKDOWN,
        open_discussion=False,
        burn_after_reading=False,
        time_to_live=timedelta(days=1),
    )
    assert Paste.from_json(paste.to_json()) == paste


def test_privatebin_url_json_roundtrip() -> None:
    url = PrivateBinUrl(
        server="https://privatebin.net/",
        id="abcdef",
        passphrase="secret",
    )
    assert PrivateBinUrl.from_json(url.to_json()) == url
