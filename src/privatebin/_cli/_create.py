from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import privatebin
from privatebin import Attachment, Expiration, Feature, Formatter
from privatebin._cli._common import suppress_traceback

EXPIRATIONS = tuple(member.value for member in Expiration)
FORMATTERS = {
    "text": Formatter.PLAIN_TEXT,
    "markdown": Formatter.MARKDOWN,
    "code": Formatter.SOURCE_CODE,
}


def existing_file(value: str) -> Path:
    """Argparse type: resolve the path and reject non-existent files."""
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"'{value}' is not an existing file")
    return path


def register(parser: argparse.ArgumentParser) -> None:
    """Register the 'create' subcommand's arguments."""
    parser.add_argument(
        "-a",
        "--attachment",
        action="append",
        type=existing_file,
        help="Attachments to include with the paste (repeatable)",
    )
    parser.add_argument(
        "-b",
        "--burn",
        action="store_true",
        help="If set, the paste will be automatically deleted after the first view",
    )
    parser.add_argument(
        "-e",
        "--expiration",
        choices=EXPIRATIONS,
        default="1day",
        help="The desired expiration time for the paste (%(choices)s)",
    )
    parser.add_argument(
        "-f",
        "--formatter",
        choices=FORMATTERS.keys(),
        default="text",
        help="The formatting option for the paste content (%(choices)s)",
    )
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output paste data in JSON format"
    )
    parser.add_argument(
        "-p",
        "--password",
        help="A password to encrypt the paste with an additional layer of security",
    )
    parser.add_argument(
        "-s",
        "--server",
        default=os.environ.get("PRIVATEBIN_SERVER", "https://privatebin.net/"),
        help="The base URL of the PrivateBin instance to use",
    )
    parser.add_argument("text", nargs="?", default=None, help="The text content of the paste")


@suppress_traceback
def run(args: argparse.Namespace) -> int:
    attachments = (
        tuple(Attachment.from_file(file) for file in args.attachment)  # pyrefly: ignore[unknown-argument-type]
        if args.attachment
        else None
    )
    text = args.text if args.text is not None else sys.stdin.buffer.read().decode()

    receipt = privatebin.create(
        text=text.strip(),
        server=args.server,  # pyrefly: ignore[unknown-argument-type]
        attachments=attachments,
        password=args.password,  # pyrefly: ignore[unknown-argument-type]
        feature=Feature.BURN_AFTER_READING if args.burn else None,
        expiration=Expiration(args.expiration),  # pyrefly: ignore[unknown-argument-type]
        formatter=FORMATTERS[args.formatter],
    )

    if args.json:
        print(receipt.to_json())
    else:
        print(receipt.url.unmask())

    return 0
