from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from privatebin._cli import _create, _delete, _get
from privatebin._cli._help import ClapLikeHelpFormatter
from privatebin._version import __version__

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from typing_extensions import Self

__all__ = ("main",)


class PrivateBinArgumentParser(argparse.ArgumentParser):
    """
    Thin ArgumentParser subclass that exists to configure
    ClapLikeHelpFormatter and the default -h/--help flag.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            formatter_class=ClapLikeHelpFormatter,
            add_help=False,
            **kwargs,
        )
        self.add_argument("-h", "--help", action="help", help="Print help")

    @classmethod
    def new(cls) -> Self:
        parser = cls(
            prog="privatebin",
            description="Command line interface to the PrivateBin API",
            usage="%(prog)s [-h] [--version] [create | get | delete] ...",
        )
        parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"%(prog)s {__version__}",
            help="Print version",
        )
        subparsers = parser.add_subparsers(
            title="commands",
            dest="command",
            required=True,
            # On Python <3.14, argparse inherits the parent's full usage
            # string here, resulting in:
            # "privatebin [-h] [--version] [create | get | delete] ... create [-h] ..."
            # Passing "privatebin" explicitly gives us the shorter:
            # "privatebin create [-h] ..."
            prog="privatebin",
        )

        _create.register(
            subparsers.add_parser(
                "create",
                help="Create a new paste on PrivateBin",
            )
        )
        _delete.register(
            subparsers.add_parser(
                "delete",
                help="Delete a paste from PrivateBin using its URL and delete token",
            )
        )
        _get.register(
            subparsers.add_parser(
                "get",
                help="Retrieve and decrypt a paste from a PrivateBin URL",
            )
        )
        # Re-arrange sections to match clap
        positionals, optionals, commands = parser._action_groups
        parser._action_groups = [commands, positionals, optionals]
        return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = PrivateBinArgumentParser.new().parse_args(argv)
    match args.command:
        case "create":
            return _create.run(args)
        case "delete":
            return _delete.run(args)
        case "get":
            return _get.run(args)
        case _ as unreachable:
            raise AssertionError(f"Unreachable command: {unreachable}")
