from __future__ import annotations

from privatebin._utils import Zlib, guess_mime_type, to_compact_json


def test_zlib() -> None:
    original = b"Hello World!"
    compressed = Zlib(original).compress()
    decompressed = Zlib(compressed).decompress()
    assert original == decompressed


def test_to_compact_json() -> None:
    data = [
        ["EhGlr6MDIrNHFyhdMAE6gA==", "wATfGNcSqjM=", 100000, 256, 128, "aes", "gcm", "zlib"],
        "plaintext",
        0,
        0,
    ]

    assert (
        to_compact_json(data)
        == '[["EhGlr6MDIrNHFyhdMAE6gA==","wATfGNcSqjM=",100000,256,128,"aes","gcm","zlib"],"plaintext",0,0]'
    )


def test_guess_mime_type() -> None:
    assert guess_mime_type("hello.txt") == "text/plain"
    assert guess_mime_type("LICENSE") == "application/octet-stream"
