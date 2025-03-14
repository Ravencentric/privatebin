from __future__ import annotations

import rich
from cyclopts import App

import privatebin

delete_app = App(
    "delete",
    help="Delete a paste from PrivateBin using its URL and delete token.",
)


@delete_app.default
def delete(
    url: str,
    /,
    *,
    token: str,
) -> int:
    """
    Delete a paste from PrivateBin using its URL and delete token.

    Parameters
    ----------
    url : str
        The complete URL of the PrivateBin paste, with or without the passphrase.
    token : str
        The delete token associated with the paste.

    """
    try:
        url = url.strip()
        privatebin.delete(url, delete_token=token)
        return 0
    except Exception as e:
        rich.print(f"[red]Error:[/] {e}")
        return 1
