from __future__ import annotations

import types

import pytest

import privatebin


@pytest.mark.parametrize("name", privatebin.__all__)
def test_every_all_name_is_exported(name: str) -> None:
    value = getattr(privatebin, name)
    if name == "__version__":
        assert isinstance(value, str)
    else:
        assert isinstance(value, (type, types.FunctionType))


def test_unknown_attribute_raises() -> None:
    with pytest.raises(AttributeError, match="has no attribute 'foobar'"):
        _ = privatebin.foobar


def test_dir_matches_all() -> None:
    assert dir(privatebin) == sorted(privatebin.__all__)
