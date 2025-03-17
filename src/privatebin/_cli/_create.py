from __future__ import annotations

import json as _json
import sys
from typing import Annotated, Literal

import rich
from cyclopts import App, Parameter
from cyclopts.types import ResolvedExistingFile  # noqa: TC002

import privatebin
from privatebin import Attachment, Expiration, Formatter

create_app = App(
    "create",
    help="Create a new paste on PrivateBin.",
)


@create_app.default
def create(  # noqa: PLR0913
    text: str | None = None,
    /,
    *,
    server: Annotated[
        str, Parameter(name=["--server", "-s"], env_var="PRIVATEBIN_SERVER")
    ] = "https://privatebin.net/",
    attachment: Annotated[
        ResolvedExistingFile | None, Parameter(name=["--attachment", "-a"])
    ] = None,
    password: Annotated[str | None, Parameter(name=["--password", "-p"])] = None,
    burn: bool = False,
    expiration: Annotated[
        Literal["5min", "10min", "1hour", "1day", "1week", "1month", "1year", "never"],
        Parameter(name=["--expiration", "-e"]),
    ] = "1week",
    formatter: Annotated[
        Literal["text", "markdown", "code"], Parameter(name=["--formatter", "-f"])
    ] = "text",
    json: bool = False,
    pretty: bool = False,
) -> int:
    """
    Create a new paste on PrivateBin.

    Parameters
    ----------
    text : str, optional
        The text content of the paste.
    server : str, optional
        The base URL of the PrivateBin instance to use.
    attachment : ResolvedExistingFile, optional
        An attachment to include with the paste.
    password : str, optional
        A password to encrypt the paste with an additional layer of security.
    burn : bool, optional
        If set, the paste will be automatically deleted after the first view.
    expiration : Literal["5min", "10min", "1hour", "1day", "1week", "1month", "1year", "never"], optional
        The desired expiration time for the paste.
    formatter : Literal["text", "markdown", "code"], optional
        The formatting option for the paste content.
    json : bool, optional
        Output paste data in JSON format.
    pretty : bool, optional
        Pretty-print JSON output.

    """
    try:
        _attachment = Attachment.from_file(attachment) if attachment else None

        if text is None:
            text = sys.stdin.buffer.read().decode(encoding="utf-8")

        _formatter_map = {
            "text": Formatter.PLAIN_TEXT,
            "markdown": Formatter.MARKDOWN,
            "code": Formatter.SOURCE_CODE,
        }

        url = privatebin.create(
            text=text.strip(),
            server=server,
            attachment=_attachment,
            password=password,
            burn_after_reading=burn,
            expiration=Expiration(expiration),
            formatter=_formatter_map[formatter],
        )

        _dict = url.model_dump(mode="json")
        _dict["url"] = url.to_str()
        _rejson = _json.dumps(_dict, indent=2)

        if json:
            if pretty:
                rich.print_json(_rejson)
            else:
                print(_rejson)
        else:
            print(url.to_str())

        return 0

    except Exception as e:
        rich.print(f"[red]Error:[/] {e}")
        return 1
