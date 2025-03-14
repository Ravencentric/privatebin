# privatebin

[![PyPI - Version](https://img.shields.io/pypi/v/privatebin?link=https%3A%2F%2Fpypi.org%2Fproject%2Fprivatebin%2F)](https://pypi.org/project/privatebin/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/privatebin)
![License](https://img.shields.io/github/license/Ravencentric/privatebin)
![PyPI - Types](https://img.shields.io/pypi/types/privatebin)

![GitHub Build Workflow Status](https://img.shields.io/github/actions/workflow/status/Ravencentric/privatebin/release.yml)
![GitHub Tests Workflow Status](https://img.shields.io/github/actions/workflow/status/ravencentric/privatebin/tests.yml?label=tests)
[![codecov](https://codecov.io/gh/Ravencentric/privatebin/graph/badge.svg?token=L1ZPQCVNDG)](https://codecov.io/gh/Ravencentric/privatebin)

Python library for interacting with PrivateBin's v2 API (PrivateBin >= 1.3) to create, retrieve, and delete encrypted pastes.

## Installation

`privatebin` is available on [PyPI](https://pypi.org/project/privatebin/), so you can simply use [pip](https://github.com/pypa/pip) to install it.

1. To install the core library:

    ```sh
    pip install privatebin
    ```

2. To install the CLI:

    - With [`pipx`](https://pipx.pypa.io/stable/) or [`uv`](https://docs.astral.sh/uv/guides/tools/#installing-tools) (recommended)

        ```sh
        pipx install "privatebin[cli]"
        ```
        ```sh
        uv tool install "privatebin[cli]"
        ```

    - With [`pip`](https://pip.pypa.io/en/stable/installation/)

        ```sh
        pip install "privatebin[cli]"
        ```

## Docs

Checkout the [quick start page](https://privatebin.ravencentric.cc/quick-start/) and the [API reference](https://privatebin.ravencentric.cc/api-reference/client/).

## License

Distributed under the [MIT](https://choosealicense.com/licenses/mit/) License. See [LICENSE](https://github.com/Ravencentric/privatebin/blob/main/LICENSE) for more information.
