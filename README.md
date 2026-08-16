# privatebin

[![PyPI - Version](https://img.shields.io/pypi/v/privatebin?link=https%3A%2F%2Fpypi.org%2Fproject%2Fprivatebin%2F)](https://pypi.org/project/privatebin/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/privatebin)
![License](https://img.shields.io/github/license/Ravencentric/privatebin)
![PyPI - Types](https://img.shields.io/pypi/types/privatebin)

![GitHub Build Workflow Status](https://img.shields.io/github/actions/workflow/status/Ravencentric/privatebin/release.yml)
![GitHub Tests Workflow Status](https://img.shields.io/github/actions/workflow/status/ravencentric/privatebin/tests.yml?label=tests)
[![codecov](https://codecov.io/gh/Ravencentric/privatebin/graph/badge.svg?token=L1ZPQCVNDG)](https://codecov.io/gh/Ravencentric/privatebin)

Python library for interacting with PrivateBin's v2 API (PrivateBin >= 1.3) to create,
retrieve, and delete encrypted pastes.

## Installation

`privatebin` is available on [PyPI](https://pypi.org/project/privatebin/), so you can
simply use [pip](https://github.com/pypa/pip) to install it.

```sh
pip install privatebin
```

## Docs

Checkout the [quick start page](https://ravencentric.cc/privatebin/quick-start/) and the
[API reference](https://ravencentric.cc/privatebin/api-reference/client/).

## Development

This is a pure-Python project, so development is pretty straightforward.
I use [`uv`](https://docs.astral.sh/uv/) to manage the project.

Linting, formatting, and type checking is handled by Ruff and Pyrefly:

```text
uv run ruff check
uv run ruff format
uv run pyrefly check
```

Fairly standard stuff. The tests are a bit more interesting.
They run entirely offline (thanks to `pytest-socket`).

Running the unit tests is as easy as:

```text
uv run pytest
```

Then there is the integration suite, which runs additional tests against a real instance
of PrivateBin. The instance is created automatically as long as you have Docker or
Podman available via `./docker/compose.yaml` and is cleaned up afterwards.

```text
uv run pytest --integration
```

This will fail if you have neither Docker nor Podman. By default, it uses the port
`59483`, but you can change it easily:

```text
uv run pytest --integration --port 8080
```

I also support passing any HTTP client that satisfies the
[`HttpClientProtocol`](https://ravencentric.cc/privatebin/api-reference/protocols/#privatebin._protocols.HttpClientProtocol).
The integration tests only run against the default HTTP client by default. You can also
run them against several other HTTP clients that I test for protocol compatibility with:

```text
uv run pytest --integration --all-http-clients
```

## License

Distributed under the [MIT](https://choosealicense.com/licenses/mit/) License. See
[LICENSE](https://github.com/Ravencentric/privatebin/blob/main/LICENSE) for more
information.
