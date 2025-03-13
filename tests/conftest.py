from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from privatebin import PrivateBin

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def pbin_client() -> Iterator[PrivateBin]:
    with PrivateBin() as client:
        yield client
