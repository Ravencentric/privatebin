from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Protocol

import privatebin
from privatebin import Attachment, Expiration, Feature, Formatter

EXPIRATIONS = tuple(member.value for member in Expiration)

FORMATTERS = {
    "text": Formatter.PLAIN_TEXT,
    "markdown": Formatter.MARKDOWN,
    "code": Formatter.SOURCE_CODE,
}


class CreateArgs(Protocol):
    """Shape of the parsed 'create' arguments."""

    text: str | None
    server: str
    attachment: list[Path] | None
    password: str | None
    burn: bool
    expiration: str
    formatter: str
    json: bool


def existing_file(value: str) -> Path:
    """Argparse type: resolve the path and reject non-existent files."""
    file = Path(value).expanduser().resolve()
    if not file.is_file():
        raise argparse.ArgumentTypeError(f"'{value}' is not an existing file")
    return file


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
        default="1week",
        help="The desired expiration time for the paste (%(choices)s)",
    )
    parser.add_argument(
        "-f",
        "--formatter",
        choices=("text", "markdown", "code"),
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


def run(args: CreateArgs) -> int:
    try:
        attachments = (
            tuple(Attachment.from_file(file) for file in args.attachment)
            if args.attachment
            else None
        )
        text = args.text if args.text is not None else sys.stdin.buffer.read().decode()

        receipt = privatebin.create(
            text=text.strip(),
            server=args.server,
            attachments=attachments,
            password=args.password,
            feature=Feature.BURN_AFTER_READING if args.burn else None,
            expiration=Expiration(args.expiration),
            formatter=FORMATTERS[args.formatter],
        )

        if args.json:
            print(receipt.to_json())
        else:
            print(receipt.url.unmask())

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
