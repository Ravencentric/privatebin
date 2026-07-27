from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

import httpx
import pytest

from privatebin import PrivateBin

if TYPE_CHECKING:
    from collections.abc import Iterator


def get_container_runtime() -> str:
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
    assert httpx.get(server).status_code == 200, "PrivateBin instance is unhealthy."
    try:
        yield server
    finally:
        subprocess.run((*args, "down", "--volumes"), check=False)


@pytest.fixture
def pbin_client(server: str) -> Iterator[PrivateBin]:
    with PrivateBin(server) as client:
        yield client
