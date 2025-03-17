from __future__ import annotations

from pathlib import Path

import tomli

from privatebin._version import __version__


def test_version() -> None:
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject.is_file()
    with open(pyproject, "rb") as f:
        version = tomli.load(f)["project"]["version"]

    assert version == __version__
