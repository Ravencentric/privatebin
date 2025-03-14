from __future__ import annotations

import sys
from enum import IntEnum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from stringenum import StrEnum

# Enums based on PrivateBin's types.jsonld:
# Reference: https://raw.githubusercontent.com/PrivateBin/PrivateBin/master/js/types.jsonld


class Formatter(StrEnum):
    """Formatting options for PrivateBin content."""

    PLAIN_TEXT = "plaintext"
    SOURCE_CODE = "syntaxhighlighting"
    MARKDOWN = "markdown"


class Compression(StrEnum):
    """Compression algorithms for PrivateBin."""

    ZLIB = "zlib"
    NONE = "none"


class Expiration(StrEnum):
    """
    Paste expiration durations for PrivateBin.

    Notes
    -----
    Not every PrivateBin instance may support all of these expiration options.

    """

    FIVE_MIN = "5min"
    TEN_MIN = "10min"
    ONE_HOUR = "1hour"
    ONE_DAY = "1day"
    ONE_WEEK = "1week"
    ONE_MONTH = "1month"
    ONE_YEAR = "1year"
    NEVER = "never"


class PrivateBinEncryptionSetting(IntEnum):
    """Encryption parameters for PrivateBin."""

    # "A good default is at least 1,000,000 iterations" - https://cryptography.io/en/latest/fernet/
    ITERATIONS = 1_000_000
    SALT_SIZE = 8  # Allowed: 8 (According to my own tests.)
    KEY_SIZE = 256  # Allowed: [128, 196, 256] (as per PrivateBin)
    TAG_SIZE = 128  # Allowed: [64, 96, 104, 112, 120, 128] (as per PrivateBin)
