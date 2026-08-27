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

Linting, formatting, and type checking are handled by Ruff and Pyrefly:

```text
uv run ruff check
uv run ruff format
uv run pyrefly check
```

The testing story is a bit more interesting because the test suite runs entirely
offline.

Simply invoking pytest will run all the unit tests:

```text
uv run pytest
```

Tacking on `--integration` to that will run the integration tests, which reside in
`tests\integration`, against a real instance of PrivateBin. This instance will be
created automatically as long as you have Docker or Podman available (it will fail
otherwise) via `./docker/compose.yaml`, and is cleaned up afterwards.
By default, it uses port `59483`, but you can pass a different one:

```text
uv run pytest --integration --port 54748
```

I also support passing any HTTP client that satisfies the
[`HttpClientProtocol`](https://ravencentric.cc/privatebin/api-reference/protocols/#privatebin._protocols.HttpClientProtocol),
but the integration tests only run against the default HTTP client by default.

You'll have to pass `--all-http-clients` to run the integration tests against
several other HTTP clients that I test for protocol compatibility with:

```text
uv run pytest --integration --all-http-clients
```

Note that the specific HTTP clients are not documented because the goal is to support
the interface rather than any particular implementation.

## License

Distributed under the [MIT](https://choosealicense.com/licenses/mit/) License. See
[LICENSE](https://github.com/Ravencentric/privatebin/blob/main/LICENSE) for more
information.
