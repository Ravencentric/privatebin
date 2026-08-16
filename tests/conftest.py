from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest import Config, Item


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests against a PrivateBin test instance running on localhost",
    )
    parser.addoption(
        "--all-http-clients",
        action="store_true",
        default=False,
        help="Run integration tests parametrized over all supported HTTP clients",
    )
    parser.addoption(
        "--port",
        type=int,
        default=59483,
        help="Port on localhost for the PrivateBin test instance (default: 59483)",
    )


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """
    Automatically apply @pytest.mark.integration to every test
    located under tests/integration/.
    """
    integration = config.getoption("--integration") or config.getoption("--all-http-clients")
    skip = pytest.mark.skip(reason="Pass --integration or --all-http-clients to run")
    dir = Path(__file__).parent / "integration"

    for item in items:
        if item.path.is_relative_to(dir):
            item.add_marker("integration")
            if not integration:
                item.add_marker(skip)
