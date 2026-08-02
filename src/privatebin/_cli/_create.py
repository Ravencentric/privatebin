from __future__ import annotations

import sys
from typing import Annotated, Literal

import rich
from cyclopts import App, Parameter
from cyclopts.types import ResolvedExistingFile

import privatebin
from privatebin import Attachment, Expiration, Formatter, Mode

create_app = App(
    "create",
    help="Create a new paste on PrivateBin.",
)


@create_app.default
def create(
    text: str | None = None,
    /,
    *,
    server: Annotated[
        str, Parameter(name=["--server", "-s"], env_var="PRIVATEBIN_SERVER")
    ] = "https://privatebin.net/",
    attachments: Annotated[
        list[ResolvedExistingFile] | None, Parameter(name=["--attachment", "-a"])
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
    attachments : list[ResolvedExistingFile], optional
        Attachments to include with the paste.
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
        _attachments = (
            tuple(Attachment.from_file(file) for file in attachments) if attachments else None
        )

        if text is None:
            text = sys.stdin.buffer.read().decode(encoding="utf-8")

        _formatter_map = {
            "text": Formatter.PLAIN_TEXT,
            "markdown": Formatter.MARKDOWN,
            "code": Formatter.SOURCE_CODE,
        }

        paste = privatebin.create(
            text=text.strip(),
            server=server,
            attachments=_attachments,
            password=password,
            mode=Mode.BURN_AFTER_READING if burn else None,
            expiration=Expiration(expiration),
            formatter=_formatter_map[formatter],
        )

        if json:
            if pretty:
                rich.print_json(paste.to_json())
            else:
                print(paste.to_json())
        else:
            print(paste.url.unmask())

        return 0

    except Exception as e:
        rich.print(f"[red]Error:[/] {e}")
        return 1
