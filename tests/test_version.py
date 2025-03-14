from __future__ import annotations

from pathlib import Path

import tomli

import privatebin


def test_version() -> None:
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject.is_file()
    with open(pyproject, "rb") as f:
        version = tomli.load(f)["project"]["version"]

    assert version == privatebin.__version__
