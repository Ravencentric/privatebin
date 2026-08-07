from __future__ import annotations

import argparse
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
        # Pad long-only flags so they align with flags that also have a short name:
        #
        #     -h, --help
        #         --version
        #
        # Without the padding, "--version" would start one column to the left.
        if len(action.option_strings) == 1 and action.option_strings[0].startswith("--"):
            return "    " + super()._format_action_invocation(action)
        return super()._format_action_invocation(action)

    def _format_action(self, action: argparse.Action) -> str:
        # argparse prints a "{create,delete,get}" row with subcommands
        # indented below it. Print each subcommand as its own plain line instead.
        if isinstance(action, argparse._SubParsersAction):
            return "".join(
                self._format_action(subaction) for subaction in action._get_subactions()
            )
        return super()._format_action(action)
