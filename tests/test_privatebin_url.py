from __future__ import annotations

import pytest

from privatebin import PasteReceipt, PrivateBinUrl


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://privatebin.net/?926bdda997f89847#7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb",
            PrivateBinUrl(
                server="https://privatebin.net/",
                id="926bdda997f89847",
                passphrase="7GudBkzM2j27BAG5NZVDzQG1NKBGQtMqCsq84vzq4Zeb",
            ),
        ),
        (
            "https://bin.disroot.org/?4d7bc697fdea1c28#-DG2Snjk96vLtzPHLgtidHzAyL1pzKY6fru8KrsUY7Nzj",
            PrivateBinUrl(
                server="https://bin.disroot.org/",
                id="4d7bc697fdea1c28",
                passphrase="DG2Snjk96vLtzPHLgtidHzAyL1pzKY6fru8KrsUY7Nzj",
            ),
        ),
        (
            "https://0.0g.gg/?2f03f0f4297cc91e#Ek1V4dtDpgjB2xngv6Wz5m1iMGNoB6EvRswcEEjMUFMk",
            PrivateBinUrl(
                server="https://0.0g.gg/",
                id="2f03f0f4297cc91e",
                passphrase="Ek1V4dtDpgjB2xngv6Wz5m1iMGNoB6EvRswcEEjMUFMk",
            ),
        ),
        (
            "https://privatebin.arch-linux.cz/?f73477514b655dbf#-A751k9CWbR5Y5UiYb7VmK2x5HwXqETABXoCTYuPt9t9a",
            PrivateBinUrl(
                server="https://privatebin.arch-linux.cz/",
                id="f73477514b655dbf",
                passphrase="A751k9CWbR5Y5UiYb7VmK2x5HwXqETABXoCTYuPt9t9a",
            ),
        ),
    ],
)
def test_privatebin_url(url: str, expected: PrivateBinUrl) -> None:
    assert PrivateBinUrl.parse(url) == expected


def test_privatebin_url_eq() -> None:
    original = PrivateBinUrl.parse(
        "https://bin.disroot.org/?4d7bc697fdea1c28#-DG2Snjk96vLtzPHLgtidHzAyL1pzKY6fru8KrsUY7Nzj"
    )
    assert original == PrivateBinUrl.parse(
        "https://bin.disroot.org/?4d7bc697fdea1c28#DG2Snjk96vLtzPHLgtidHzAyL1pzKY6fru8KrsUY7Nzj"
    )
    receipt = PasteReceipt(url=original, delete_token="blah")
    assert PrivateBinUrl.parse(original) == PrivateBinUrl.parse(receipt) == original


def test_privatebin_url_error() -> None:
    with pytest.raises(ValueError):
        PrivateBinUrl.parse("https://example.com")

    with pytest.raises(TypeError):
        PrivateBinUrl.parse(None)  # type: ignore[arg-type]
