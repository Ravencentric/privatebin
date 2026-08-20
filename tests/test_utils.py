from __future__ import annotations

import types

import pytest

from privatebin import Compression
from privatebin._utils import Compressor, assert_type, guess_mime_type, to_compact_jsonb


@pytest.mark.parametrize("mode", tuple(Compression))
def test_compressor(mode: Compression) -> None:
    original = b"Hello World!"
    compressed = Compressor(mode=mode).compress(original)
    decompressed = Compressor(mode=mode).decompress(compressed)
    assert original == decompressed


def test_bad_compression() -> None:
    with pytest.raises(
        TypeError,
        match="Unsupported compression mode: 'foobar'. Supported modes are: 'ZLIB', 'NONE'",
    ):
        Compressor(mode="foobar").compress(b"Hello World!")  # pyrefly: ignore[bad-argument-type]

    with pytest.raises(
        TypeError,
        match="Unsupported compression mode: 'foobar'. Supported modes are: 'ZLIB', 'NONE'",
    ):
        Compressor(mode="foobar").decompress(b"Hello World!")  # pyrefly: ignore[bad-argument-type]


def test_to_compact_json() -> None:
    data = [
        ["EhGlr6MDIrNHFyhdMAE6gA==", "wATfGNcSqjM=", 100000, 256, 128, "aes", "gcm", "zlib"],
        "plaintext",
        0,
        0,
    ]

    assert (
        to_compact_jsonb(data)
        == b'[["EhGlr6MDIrNHFyhdMAE6gA==","wATfGNcSqjM=",100000,256,128,"aes","gcm","zlib"],"plaintext",0,0]'
    )


def test_to_compact_json_unicode() -> None:
    data = {"paste": "café 🎉 日本語"}
    encoded = to_compact_jsonb(data)
    assert encoded == '{"paste":"café 🎉 日本語"}'.encode()
    assert b"\\u" not in encoded


def test_guess_mime_type() -> None:
    assert guess_mime_type("hello.txt") == "text/plain"
    assert guess_mime_type("LICENSE") == "application/octet-stream"


def test_assert_type() -> None:
    with pytest.raises(TypeError, match="Parameter 'foo' expected 'int', but got 'str'."):
        assert_type("", int, param="foo")

    with pytest.raises(
        TypeError,
        match="Parameter 'foo' expected one of the following types: 'int', 'NoneType', but got 'str'.",
    ):
        assert_type("", (int, types.NoneType), param="foo")
