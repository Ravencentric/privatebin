from __future__ import annotations

try:
    from cyclopts import App
except ModuleNotFoundError:
    import sys

    print(
        "Error: Required dependencies for the CLI are missing. "
        "Install `privatebin[cli]` to fix this."
    )
    sys.exit(1)

import privatebin
from privatebin._cli import create_app, delete_app, get_app

app = App(
    "privatebin",
    help="Command line interface to the PrivateBin API.",
    version=privatebin.__version__,
)

app.command(create_app)
app.command(delete_app)
app.command(get_app)

if __name__ == "__main__":
    app()
