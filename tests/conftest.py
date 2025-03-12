from __future__ import annotations

from collections.abc import Iterator

import pytest

from privatebin import PrivateBin


@pytest.fixture
def pbin_client() -> Iterator[PrivateBin]:
    with PrivateBin() as client:
        yield client
