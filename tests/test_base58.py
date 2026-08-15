from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from privatebin._base58 import BASE58_ALPHABET, b58decode, b58encode


@pytest.mark.parametrize(
    ("raw", "encoded"),
    [
        (b"", ""),
        (b"\x00", "1"),
        (b"\x01", "2"),
        (b"\x00\x00\x00", "111"),
        (b"hello", "Cn8eVZg"),
        (b"\x00\x00hello", "11Cn8eVZg"),
    ],
)
def test_base58_roundtrip(raw: bytes, encoded: str) -> None:
    assert b58encode(raw) == encoded
    assert b58decode(encoded) == raw


@given(raw=st.binary())
@settings(max_examples=1000)
def test_base58_decode_is_inverse_of_encode(raw: bytes) -> None:
    assert b58decode(b58encode(raw)) == raw


@given(encoded=st.text(alphabet=BASE58_ALPHABET))
@settings(max_examples=1000)
def test_base58_encode_is_inverse_of_decode(encoded: str) -> None:
    assert b58encode(b58decode(encoded)) == encoded


@given(raw=st.binary())
@settings(max_examples=1000)
def test_base58_encoded_only_uses_alphabet(raw: bytes) -> None:
    assert set(b58encode(raw)) <= set(BASE58_ALPHABET)


@given(raw=st.binary(), padding=st.integers(min_value=0, max_value=8))
@settings(max_examples=1000)
def test_base58_leading_zero_bytes(raw: bytes, padding: int) -> None:
    assert b58encode(b"\x00" * padding + raw) == "1" * padding + b58encode(raw)


def test_b58decode_rejects_whitespace() -> None:
    with pytest.raises(ValueError, match="Non-base58 character"):
        b58decode("Cn8eVZg  ")


def test_b58decode_invalid_character() -> None:
    with pytest.raises(ValueError, match="Non-base58 character"):
        b58decode("0")
