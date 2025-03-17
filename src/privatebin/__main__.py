from __future__ import annotations

try:
    from cyclopts import App, Parameter
except ModuleNotFoundError:
    import sys

    print(
        "Error: Required dependencies for the CLI are missing. "
        "Install `privatebin[cli]` to fix this."
    )
    sys.exit(1)

from privatebin._cli import create_app, delete_app, get_app
from privatebin._version import __version__

app = App(
    "privatebin",
    help="Command line interface to the PrivateBin API.",
    version=__version__,
    default_parameter=Parameter(negative=""),
)

app.command(create_app)
app.command(delete_app)
app.command(get_app)

if __name__ == "__main__":
    app()
