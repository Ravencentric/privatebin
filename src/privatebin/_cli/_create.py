from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import privatebin
from privatebin import Expiration, Feature, Formatter

SERVER = "https://privatebin.net/"
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
        default=[],
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
        default=os.environ.get("PRIVATEBIN_SERVER", SERVER),
        help="The base URL of the PrivateBin instance to use (env: PRIVATEBIN_SERVER) (default: %(default)s)",
    )
    parser.add_argument("text", nargs="?", default=None, help="The text content of the paste")


def ensure_default_instance_supports(server: str, expiration: Expiration) -> None:
    """
    PrivateBin doesn't reject invalid expirations, it just uses the
    instance's default expiration upon encountering an unsupported expiration.
    Can't do much about arbitrary servers but we do know what the default instance
    supports so we can error early.
    """
    if server.rstrip("/") != SERVER.rstrip("/"):
        return

    if expiration not in (
        Expiration.FIVE_MIN,
        Expiration.TEN_MIN,
        Expiration.ONE_HOUR,
        Expiration.ONE_DAY,
    ):
        raise ValueError(
            f"\nThe default PrivateBin instance ({SERVER}) only supports "
            "expirations of up to 1 day.\n"
            "Use -s/--server to select a PrivateBin instance whose limits "
            "meet your preferences."
        )


def run(args: argparse.Namespace) -> int:
    try:
        ensure_default_instance_supports(
            server=args.server,
            expiration=Expiration(args.expiration),
        )

        attachments = tuple(privatebin.Attachment.from_file(file) for file in args.attachment)
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
