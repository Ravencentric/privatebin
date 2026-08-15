from __future__ import annotations

from typing import Final

# The Bitcoin alphabet PrivateBin's web client uses for passphrases
# Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/privatebin.js#L986>
BASE58_ALPHABET: Final = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
FIRST_CHAR: Final = BASE58_ALPHABET[0]
NULL = b"\x00"


# Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L24>
def b58encode(raw: bytes, /) -> str:
    """Encode bytes to a Base58 string."""
    value = int.from_bytes(raw, "big")

    digits: list[str] = []

    while value > 0:
        value, remainder = divmod(value, 58)
        digits.append(BASE58_ALPHABET[remainder])
    digits.reverse()

    # Map leading zero bytes to FIRST_CHAR
    # Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L65>
    leading_zero_bytes = len(raw) - len(raw.lstrip(NULL))
    return FIRST_CHAR * leading_zero_bytes + "".join(digits)


def b58decode(encoded: str, /) -> bytes:
    """Decode a Base58 string to bytes."""
    value = 0
    for character in encoded:
        try:
            value = value * 58 + BASE58_ALPHABET.index(character)
        except ValueError:
            msg = "Non-base58 character"
            raise ValueError(msg) from None

    byte_length = (value.bit_length() + 7) // 8
    decoded = value.to_bytes(byte_length, "big")

    # Map leading FIRST_CHAR(s) back to `\x00` bytes
    # Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L73-L79>
    # Ref: <https://github.com/PrivateBin/PrivateBin/blob/0e81e5a4e8546b30e9d8736e5bff1506e9530130/js/base-x-5.0.1.js#L108>
    leading_zero_bytes = len(encoded) - len(encoded.lstrip(FIRST_CHAR))
    return NULL * leading_zero_bytes + decoded
