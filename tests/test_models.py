from __future__ import annotations

import base64
import re
from typing import TYPE_CHECKING

import pytest

from privatebin import Attachment

if TYPE_CHECKING:
    from pathlib import Path


def test_attachment_from_file(tmp_path: Path) -> None:
    file = tmp_path / "attachment.txt"
    file.write_bytes(b"hello from attachment")

    attachment = Attachment.from_file(file)
    assert attachment.name == "attachment.txt"
    assert attachment.content == b"hello from attachment"

    assert attachment.to_base64_data_url() == "data:text/plain;base64,aGVsbG8gZnJvbSBhdHRhY2htZW50"
    assert (
        attachment.model_dump_json()
        == '{"content":"data:text/plain;base64,aGVsbG8gZnJvbSBhdHRhY2htZW50","name":"attachment.txt"}'
    )


def test_attachment_from_file_with_different_name(tmp_path: Path) -> None:
    file = tmp_path / "attachment.txt"
    file.write_bytes(b"hello from attachment")

    attachment = Attachment.from_file(file, name="hello.txt")
    assert attachment.name == "hello.txt"
    assert attachment.content == b"hello from attachment"

    assert attachment.to_base64_data_url() == "data:text/plain;base64,aGVsbG8gZnJvbSBhdHRhY2htZW50"


def test_attachment_from_file_error(tmp_path: Path) -> None:
    file = tmp_path / "attachment.txt"

    with pytest.raises(FileNotFoundError, match=re.escape(str(file))):
        Attachment.from_file(file)


def test_attachment_from_b64() -> None:
    original = b"Foo and bar"
    data = base64.b64encode(original).decode()

    attachment = Attachment.from_base64_data_url(
        content=f"data:application/octet-stream;base64,{data}", name="baz"
    )
    assert attachment.name == "baz"
    assert attachment.content == b"Foo and bar"

    assert (
        attachment.to_base64_data_url() == "data:application/octet-stream;base64,Rm9vIGFuZCBiYXI="
    )


def test_attachment_from_b64_error() -> None:
    original = b"Foo and bar"
    data = base64.b64encode(original).decode()
    content = f"data:application/octet-stream;base65,{data}"

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Paste has an invalid or unsupported attachment. "
            "Expected format: 'data:<mimetype>;base64,<data>', got: 'data:application/octet-stream;base65,Rm9vIGFuZCBiY... (TRUNCATED)'"
        ),
    ):
        Attachment.from_base64_data_url(content=content, name="baz.txt")
