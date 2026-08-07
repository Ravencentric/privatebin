from __future__ import annotations

import sys
from collections.abc import Callable
from typing import ParamSpec

P = ParamSpec("P")


def suppress_traceback(fn: Callable[P, int]) -> Callable[P, int]:
    """
    Suppress tracebacks, print a concise error message, and return exit code 1.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    return wrapper
