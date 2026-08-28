from __future__ import annotations

from typing import Final

# The Bitcoin alphabet PrivateBin's web client uses for passphrases
# Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/privatebin.js#L986>
ALPHABET: Final = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
FIRST_CHAR: Final = ALPHABET[0]
NULL_BYTE: Final = b"\x00"
ALPHABET_MAP: Final = {c: i for i, c in enumerate(ALPHABET)}


# Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L24>
def b58encode(raw: bytes, /) -> str:
    """Encode bytes to a Base58 string."""
    if not raw:
        return ""

    value = int.from_bytes(raw, "big")

    digits: list[str] = []

    while value > 0:
        value, remainder = divmod(value, 58)
        digits.append(ALPHABET[remainder])
    digits.reverse()

    # Map leading zero bytes to `FIRST_CHAR`
    # Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L65>
    leading_zero_bytes = len(raw) - len(raw.lstrip(NULL_BYTE))
    return FIRST_CHAR * leading_zero_bytes + "".join(digits)


def b58decode(encoded: str, /) -> bytes:
    """Decode a Base58 string to bytes."""
    if not encoded:
        return b""

    value = 0
    for character in encoded:
        try:
            value = value * 58 + ALPHABET_MAP[character]
        except KeyError:
            msg = f"Non-base58 character: {character!r}"
            raise ValueError(msg) from None

    byte_length = (value.bit_length() + 7) // 8
    decoded = value.to_bytes(byte_length, "big")

    # Map leading `FIRST_CHAR`(s) back to `NULL_BYTE`(s)
    # Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L73-L79>
    # Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L108>
    leading_zero_bytes = len(encoded) - len(encoded.lstrip(FIRST_CHAR))
    return NULL_BYTE * leading_zero_bytes + decoded
