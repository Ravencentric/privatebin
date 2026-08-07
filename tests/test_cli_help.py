from __future__ import annotations

import os
import shutil
from collections.abc import Sequence
from typing import cast

import pytest

from privatebin.__main__ import main
from privatebin._version import __version__

TOP_LEVEL_HELP = """\
Usage: privatebin [-h] [--version] [create | get | delete] ...

Command line interface to the PrivateBin API

Commands:
  create               Create a new paste on PrivateBin
  delete               Delete a paste from PrivateBin using its URL and delete token
  get                  Retrieve and decrypt a paste from a PrivateBin URL

Options:
  -h, --help           Print help
      --version        Print version
"""

CREATE_HELP = """\
Usage: privatebin create [-h] [-a <ATTACHMENT>] [-b] [-e <EXPIRATION>] [-f <FORMATTER>] [-j] [-p <PASSWORD>] [-s <SERVER>] [text]

Arguments:
  text                           The text content of the paste

Options:
  -h, --help                     Print help
  -a, --attachment <ATTACHMENT>  Attachments to include with the paste (repeatable)
  -b, --burn                     If set, the paste will be automatically deleted after the first view
  -e, --expiration <EXPIRATION>  The desired expiration time for the paste (5min, 10min, 1hour, 1day, 1week, 1month, 1year, never)
  -f, --formatter <FORMATTER>    The formatting option for the paste content (text, markdown, code)
  -j, --json                     Output paste data in JSON format
  -p, --password <PASSWORD>      A password to encrypt the paste with an additional layer of security
  -s, --server <SERVER>          The base URL of the PrivateBin instance to use
"""

GET_HELP = """\
Usage: privatebin get [-h] [-j] [-p <PASSWORD>] url

Arguments:
  url                        PrivateBin URL of the paste to retrieve

Options:
  -h, --help                 Print help
  -j, --json                 Output paste data in JSON format
  -p, --password <PASSWORD>  Password for password-protected pastes
"""

DELETE_HELP = """\
Usage: privatebin delete [-h] -t <TOKEN> url

Arguments:
  url                  The complete URL of the PrivateBin paste, with or without the passphrase

Options:
  -h, --help           Print help
  -t, --token <TOKEN>  The delete token associated with the paste
"""


@pytest.fixture(autouse=True)
def fixed_terminal_width(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        shutil,
        shutil.get_terminal_size.__name__,
        lambda fallback=(200, 24): os.terminal_size((200, 24)),
    )


def cli(argv: Sequence[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    """Run the CLI, returning (exit code, stdout, stderr)."""
    with pytest.raises(SystemExit) as exc_info:
        main(argv)
    captured = capsys.readouterr()
    return cast(int, exc_info.value.code), captured.out, captured.err


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["-h"], TOP_LEVEL_HELP),
        (["--help"], TOP_LEVEL_HELP),
        (["create", "-h"], CREATE_HELP),
        (["get", "-h"], GET_HELP),
        (["delete", "-h"], DELETE_HELP),
    ],
    ids=["args: -h", "args: --help", "args: create -h", "args: get -h", "args: delete -h"],
)
def test_help(argv: list[str], expected: str, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = cli(argv, capsys)
    assert code == 0
    assert out == expected
    assert err == ""


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = cli(["--version"], capsys)
    assert code == 0
    assert out == f"privatebin {__version__}\n"
    assert err == ""
