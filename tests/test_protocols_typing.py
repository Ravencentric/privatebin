from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx
    import httpx2
    import niquests
    import requests

    from privatebin._protocols import HttpClientProtocol

    _c1: HttpClientProtocol = httpx.Client()
    _c2: HttpClientProtocol = httpx2.Client()
    _c3: HttpClientProtocol = niquests.Session()
    _c4: HttpClientProtocol = requests.Session()
