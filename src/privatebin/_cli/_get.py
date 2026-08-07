from __future__ import annotations

import argparse
from typing import Any

import privatebin
from privatebin._cli._common import suppress_traceback


def register(parser: argparse.ArgumentParser) -> None:
    """Register the 'get' subcommand's arguments."""
    parser.add_argument("url", help="PrivateBin URL of the paste to retrieve")
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output paste data in JSON format"
    )
    parser.add_argument("-p", "--password", help="Password for password-protected pastes")


@suppress_traceback
def run(args: Any) -> int:
    paste = privatebin.get(args.url.strip(), password=args.password)

    if args.json:
        print(paste.to_json())
    else:
        print(paste.text)

    return 0
