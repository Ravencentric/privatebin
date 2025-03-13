from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def decrypt(  # noqa: PLR0913
    data: bytes,
    length: int,
    salt: bytes,
    iterations: int,
    key_material: bytes,
    initialization_vector: bytes,
    associated_data: bytes,
) -> bytes:
    """
    Decrypt data using AES-GCM with a key derived from PBKDF2-HMAC.

    Parameters
    ----------
    data : bytes
        The encrypted data (ciphertext) to be decrypted.
    length : int
        The desired length of the derived key in bytes. This should match the key size
        used during encryption.
    salt : bytes
        The salt value used in the PBKDF2-HMAC key derivation process.
        This should be the same salt that was used during encryption.
    iterations : int
        The number of iterations to perform in the PBKDF2-HMAC key derivation.
        This value must match the number of iterations used during encryption.
    key_material : bytes
        The key material used as input to the PBKDF2-HMAC key derivation function.
        This is typically a passphrase or password encoded as bytes.
        This should be the same key_material that was used during encryption.
    initialization_vector : bytes
        The initialization vector (IV) or nonce used for AES-GCM decryption.
        This must be the same IV that was used during encryption.
    associated_data : bytes
        The associated data that was authenticated during encryption.
        This data is not encrypted but is included in the integrity check.
        It must be the same associated data that was used during encryption.

    Returns
    -------
    bytes
        The decrypted data as bytes.

    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(key_material)

    return AESGCM(key).decrypt(
        nonce=initialization_vector,
        data=data,
        associated_data=associated_data,
    )


def encrypt(  # noqa: PLR0913
    data: bytes,
    length: int,
    salt: bytes,
    iterations: int,
    key_material: bytes,
    initialization_vector: bytes,
    associated_data: bytes,
) -> bytes:
    """
    Encrypt data using AES-GCM with a key derived from PBKDF2-HMAC.

    Parameters
    ----------
    data : bytes
        The data to be encrypted (plaintext) as bytes.
    length : int
        The desired length of the derived key in bytes.
    salt : bytes
        A cryptographic salt, which should be randomly generated and unique for each encryption operation.
    iterations : int
        The number of iterations to perform during the PBKDF2-HMAC key derivation.
    key_material : bytes
        The secret key material used as the basis for key derivation.
        This is typically a passphrase or password encoded as bytes.
    initialization_vector : bytes
        The Initialization Vector (IV), also known as a nonce, for the AES-GCM cipher.
    associated_data : bytes
        Associated data that will be authenticated but not encrypted.

    Returns
    -------
    bytes
        The encrypted data as bytes.

    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(key_material)

    return AESGCM(key).encrypt(
        nonce=initialization_vector,
        data=data,
        associated_data=associated_data,
    )
