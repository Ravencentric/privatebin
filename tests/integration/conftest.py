from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING, Literal

import httpx
import httpx2
import niquests
import pytest
import requests

from privatebin import PrivateBin

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from privatebin._protocols import HttpClientProtocol


def get_container_runtime() -> Literal["docker", "podman"]:
    if shutil.which("docker") is not None:
        return "docker"
    if shutil.which("podman") is not None:
        return "podman"
    msg = "No container runtime found. Install docker or podman to run integration tests."
    raise RuntimeError(msg)


@pytest.fixture(scope="session")
def server() -> Iterator[str]:
    runtime = get_container_runtime()
    args = (
        runtime,
        "compose",
        "-f",
        "./docker/compose.yaml",
    )
    subprocess.run((*args, "up", "-d", "--wait"), check=True)
    server = "http://127.0.0.1:57391/"
    assert httpx2.get(server).status_code == 200, "PrivateBin instance is unhealthy."
    try:
        yield server
    finally:
        subprocess.run((*args, "down", "--volumes"), check=False)


@pytest.fixture
def client(request: pytest.FixtureRequest) -> HttpClientProtocol:
    factory: Callable[[], HttpClientProtocol] = getattr(request, "param", httpx2.Client)
    return factory()


@pytest.fixture
def pbin_client(server: str, client: HttpClientProtocol) -> Iterator[PrivateBin]:
    with PrivateBin(server, client=client) as pbin:
        yield pbin


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "client" not in metafunc.fixturenames:
        return
    if not metafunc.config.getoption("--all-http-clients"):
        return
    clients = (httpx.Client, httpx2.Client, niquests.Session, requests.Session)
    metafunc.parametrize(
        "client", clients, ids=lambda x: f"{x.__module__}.{x.__name__}", indirect=True
    )
