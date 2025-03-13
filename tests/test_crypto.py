from __future__ import annotations

import os

import pytest

from privatebin._crypto import decrypt, encrypt


@pytest.mark.parametrize("tag_size", [64, 96, 104, 112, 120, 128])
@pytest.mark.parametrize("key_length", [128, 196, 256])
def test_encrypt_decrypt_roundtrip(tag_size: int, key_length: int) -> None:
    plaintext_data = b"This is a secret message to be encrypted and decrypted."
    key_material = b"supersecretpassword"
    initialization_vector = os.urandom(tag_size // 8)
    salt = os.urandom(8)
    associated_data = b"metadata to authenticate"
    iterations = 1_000_000

    ciphertext = encrypt(
        data=plaintext_data,
        length=key_length // 8,
        salt=salt,
        iterations=iterations,
        key_material=key_material,
        initialization_vector=initialization_vector,
        associated_data=associated_data,
    )
    decrypted_plaintext = decrypt(
        data=ciphertext,
        length=key_length // 8,
        salt=salt,
        iterations=iterations,
        key_material=key_material,
        initialization_vector=initialization_vector,
        associated_data=associated_data,
    )
    assert decrypted_plaintext == plaintext_data
