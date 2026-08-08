from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import privatebin

if TYPE_CHECKING:
    import argparse


def register(parser: argparse.ArgumentParser) -> None:
    """Register the 'get' subcommand's arguments."""
    parser.add_argument("url", help="PrivateBin URL of the paste to retrieve")
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output paste data in JSON format"
    )
    parser.add_argument("-p", "--password", help="Password for password-protected pastes")


def run(args: argparse.Namespace) -> int:
    try:
        paste = privatebin.get(
            args.url.strip(),  # pyrefly: ignore[unknown-argument-type]
            password=args.password,
        )

        if args.json:
            print(paste.to_json())
        else:
            print(paste.text)

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
