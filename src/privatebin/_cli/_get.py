from __future__ import annotations

from typing import Annotated

import rich
from cyclopts import App, Parameter
from cyclopts.types import URL  # noqa: TC002

import privatebin

get_app = App(
    "get",
    help="Retrieve and decrypt a paste from a PrivateBin URL.",
)


@get_app.default
def get(
    url: URL,
    /,
    *,
    password: Annotated[str | None, Parameter(name=["--password", "-p"])] = None,
    json: bool = False,
    pretty: bool = False,
) -> int:
    """
    Retrieve and decrypt a paste from a PrivateBin URL.

    Parameters
    ----------
    url : URL
        PrivateBin URL of the paste to retrieve.
    password : str, optional
        Password for password-protected pastes.
    json : bool, optional
        Output paste data in JSON format.
    pretty : bool, optional
        Pretty-print JSON output.

    """
    try:
        paste = privatebin.get(url.strip(), password=password)

        if json:
            if pretty:
                rich.print_json(paste.model_dump_json())
            else:
                print(paste.model_dump_json(indent=2))
        else:
            print(paste.text)

        return 0

    except Exception as e:
        rich.print(f"[red]Error:[/] {e}")
        return 1
