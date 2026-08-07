from __future__ import annotations

import argparse
from typing import Any

import privatebin
from privatebin._cli._common import suppress_traceback


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
def run(args: Any) -> int:
    privatebin.delete(args.url.strip(), delete_token=args.token)
    return 0
