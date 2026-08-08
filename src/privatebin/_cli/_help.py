from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


class ClapLikeHelpFormatter(argparse.HelpFormatter):
    """
    Custom help formatter to mimic clap's help output
    (https://github.com/clap-rs/clap) because I think
    it looks better than argparse's.
    """

    def __init__(self, prog: str) -> None:
        # Give each option row enough room for the flag name and its
        # placeholder so the description starts on the same line instead of
        # wrapping onto the next one.
        super().__init__(prog, max_help_position=60)

    def start_section(self, heading: str | None) -> None:
        # Argparse names the help sections in lowercase.
        # Rename them to clap-style headings.
        match heading:
            case "positional arguments":
                heading = "Arguments"
            case "options":
                heading = "Options"
            case "commands":
                heading = "Commands"
        super().start_section(heading)

    def _format_usage(
        self,
        usage: str | None,
        actions: Iterable[argparse.Action],
        groups: Iterable[argparse._MutuallyExclusiveGroup],
        prefix: str | None,
    ) -> str:
        # Capitalize argparse's default "usage: " to match clap, but only when
        # the prefix is None. Argparse passes an empty prefix while building
        # subcommand names, and replacing it unconditionally
        # would produce "Usage: Usage: ...".
        if prefix is None:
            prefix = "Usage: "
        return super()._format_usage(usage, actions, groups, prefix)

    def _metavar_formatter(
        self, action: argparse.Action, default_metavar: str
    ) -> Callable[[int], tuple[str, ...]]:
        # Show option values in angle brackets like clap, e.g. "--formatter
        # <FORMATTER>" instead of "--formatter FORMATTER".
        # This also gets rid of choices in metavar.
        if action.metavar is None and action.option_strings:
            metavar = f"<{default_metavar}>"
            return lambda size: (metavar,) * size
        return super()._metavar_formatter(action, default_metavar)

    def _format_action_invocation(self, action: argparse.Action) -> str:
        if sys.version_info < (3, 14) and action.option_strings and action.nargs != 0:
            # Before Python 3.14, argparse repeats the metavar for each option
            # string ("-e <EXPIRATION>, --expiration <EXPIRATION>") instead of
            # the newer "-e, --expiration <EXPIRATION>" style. Keep the output
            # consistent across Python versions by using the newer format here.
            # This can be removed once Python <3.14 is no longer supported.
            default_metavar = self._get_default_metavar_for_optional(action)
            metavar = self._format_args(action, default_metavar=default_metavar)
            invocation = ", ".join(action.option_strings) + " " + metavar
            return invocation

        return super()._format_action_invocation(action)

    def _format_action(self, action: argparse.Action) -> str:
        # argparse prints a "{create,delete,get}" row with subcommands
        # indented below it. Print each subcommand as its own plain line instead.
        if isinstance(action, argparse._SubParsersAction):
            return "".join(
                self._format_action(subaction) for subaction in action._get_subactions()
            )
        return super()._format_action(action)
