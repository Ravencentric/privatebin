from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest import Config, Item


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests against a PrivateBin test instance running on localhost",
    )


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """
    Automatically apply @pytest.mark.integration to every test
    located under tests/integration/.
    """
    integration = config.getoption("--run-integration")
    skip = pytest.mark.skip(reason="Pass --run-integration to run")
    dir = Path(__file__).parent / "integration"

    for item in items:
        if item.path.is_relative_to(dir):
            item.add_marker("integration")
            if not integration:
                item.add_marker(skip)
