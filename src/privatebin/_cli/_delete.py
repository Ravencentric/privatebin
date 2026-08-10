from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import privatebin

if TYPE_CHECKING:
    import argparse


def register(parser: argparse.ArgumentParser) -> None:
    """Register the 'delete' subcommand's arguments."""
    parser.add_argument(
        "url",
        help="The complete URL of the PrivateBin paste, with or without the passphrase",
    )
    parser.add_argument(
        "-t", "--token", required=True, help="The delete token associated with the paste"
    )


def run(args: argparse.Namespace) -> int:
    try:
        privatebin.delete(
            args.url.strip(),  # pyrefly: ignore[unknown-argument-type]
            delete_token=args.token,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
