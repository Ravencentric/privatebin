from __future__ import annotations

from typing import TYPE_CHECKING

import privatebin
from privatebin._cli._common import suppress_traceback

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


@suppress_traceback
def run(args: argparse.Namespace) -> int:
    privatebin.delete(args.url.strip(), delete_token=args.token)  # pyrefly: ignore[unknown-argument-type]
    return 0
