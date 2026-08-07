from __future__ import annotations

import argparse
import sys
from typing import Protocol

import privatebin


class DeleteArgs(Protocol):
    """Shape of the parsed 'delete' arguments."""

    url: str
    token: str


def register(parser: argparse.ArgumentParser) -> None:
    """Register the 'delete' subcommand's arguments."""
    parser.add_argument(
        "url",
        help="The complete URL of the PrivateBin paste, with or without the passphrase",
    )
    parser.add_argument(
        "-t", "--token", required=True, help="The delete token associated with the paste"
    )


def run(args: DeleteArgs) -> int:
    try:
        privatebin.delete(args.url.strip(), delete_token=args.token)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
