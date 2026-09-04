from __future__ import annotations

import base64
import os
import re
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import pytest

from privatebin import (
    Attachment,
    Compression,
    Feature,
    Formatter,
    Paste,
    PrivateBinServerError,
)
from privatebin._models import AuthenticatedData, PasteJsonLD

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


def test_empty_attachment_data_url_roundtrip() -> None:
    attachment = Attachment(name="empty.txt", content=b"")

    assert (
        Attachment.from_data_url(url=attachment.to_data_url(), name=attachment.name) == attachment
    )


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
        attachments=(Attachment(name="baz.txt", content=b"Foo and bar"),),
        formatter=Formatter.MARKDOWN,
        feature=Feature.OPEN_DISCUSSION,
        time_to_live=timedelta(days=1),
    )
    assert Paste.from_json(paste.to_json()) == paste


def test_paste_json_roundtrip_multiple_attachments() -> None:
    paste = Paste(
        id="abcdef",
        text="hello world",
        attachments=(
            Attachment(name="baz.txt", content=b"Foo and bar"),
            Attachment(name="qux.txt", content=b"Qux"),
        ),
        formatter=Formatter.MARKDOWN,
        feature=Feature.BURN_AFTER_READING,
        time_to_live=timedelta(days=1),
    )
    assert Paste.from_json(paste.to_json()) == paste


@pytest.mark.parametrize(
    "feature",
    [
        pytest.param(None, id="default"),
        pytest.param(Feature.OPEN_DISCUSSION, id="open-discussion"),
        pytest.param(Feature.BURN_AFTER_READING, id="burn-after-reading"),
    ],
)
def test_authenticated_data_feature_roundtrip(feature: Feature | None) -> None:
    data = AuthenticatedData.new(
        initialization_vector=os.urandom(16),
        salt=os.urandom(8),
        feature=feature,
    )

    assert data.feature is feature
    assert data.open_discussion is (feature is Feature.OPEN_DISCUSSION)
    assert data.burn_after_reading is (feature is Feature.BURN_AFTER_READING)


def test_from_response_parses_full_paste_json_ld_shape() -> None:
    iv = os.urandom(16)
    salt = os.urandom(8)
    ct = os.urandom(32)

    response: dict[str, Any] = {
        "status": 0,
        "id": "4e7cea11af458924",
        "url": "/?4e7cea11af458924",
        "adata": [
            [
                base64.b64encode(iv).decode(),
                base64.b64encode(salt).decode(),
                100000,
                256,
                128,
                "aes",
                "gcm",
                "zlib",
            ],
            "plaintext",
            0,
            1,
        ],
        "meta": {"time_to_live": 86315},
        "v": 2,
        "ct": base64.b64encode(ct).decode(),
    }

    paste = PasteJsonLD.from_response(response)

    assert paste.status == 0
    assert paste.id == "4e7cea11af458924"
    assert paste.url == "/?4e7cea11af458924"
    assert paste.v == 2
    assert paste.ct == ct

    cipher_parameters = paste.adata.cipher_parameters
    assert cipher_parameters.initialization_vector == iv
    assert cipher_parameters.salt == salt
    assert cipher_parameters.iterations == 100000
    assert cipher_parameters.key_size == 256
    assert cipher_parameters.tag_size == 128
    assert cipher_parameters.algorithm == "aes"
    assert cipher_parameters.mode == "gcm"
    assert cipher_parameters.compression is Compression.ZLIB

    assert paste.adata.formatter is Formatter.PLAIN_TEXT
    assert paste.adata.open_discussion is False
    assert paste.adata.burn_after_reading is True
    assert paste.adata.feature is Feature.BURN_AFTER_READING

    assert paste.meta.time_to_live == timedelta(seconds=86315)


@pytest.mark.parametrize("version", [1, 3])
def test_from_response_unsupported_api_version(version: int) -> None:
    response: dict[str, object] = {"status": 0, "v": version}
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape(
            f"Only the v2 API is supported (PrivateBin >= 1.3). Got API version: {version}"
        ),
    ):
        PasteJsonLD.from_response(response)


def test_from_response_no_version() -> None:
    with pytest.raises(
        PrivateBinServerError,
        match=re.escape(
            "Only the v2 API is supported (PrivateBin >= 1.3). Got API version: UNKNOWN"
        ),
    ):
        PasteJsonLD.from_response({"status": 0})


def test_from_response_error() -> None:
    with pytest.raises(PrivateBinServerError, match="Something went terribly wrong!"):
        PasteJsonLD.from_response({"status": 1, "message": "Something went terribly wrong!"})


def test_from_response_error_fallback_message() -> None:
    with pytest.raises(PrivateBinServerError, match=re.escape("Failed to retrieve paste.")):
        PasteJsonLD.from_response({"status": 1})
