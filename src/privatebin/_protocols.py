from __future__ import annotations

from typing import Any, Protocol


class HeadersProtocol(Protocol):
    """Protocol for HTTP headers used internally by PrivateBin."""

    def update(self, mapping: dict[Any, Any], /) -> None:
        """Update the headers with a mapping."""
        ...


class ResponseProtocol(Protocol):
    """Protocol for HTTP responses used internally by PrivateBin."""

    def raise_for_status(self) -> Any:
        """Raise an exception if the response status indicates an error."""
        ...

    def json(self) -> Any:
        """Parse the response body as JSON."""
        ...


class HttpClientProtocol(Protocol):
    """
    Protocol defining the interface for HTTP clients compatible with PrivateBin.

    !!! note
        These Protocols exist to define [`PrivateBin`][privatebin.PrivateBin]'s
        contract with HTTP clients and aren't intended to be used directly.
        They're documented here to provide some insight into that
        contract and why it exists.

        Any object implementing this Protocol *should* be able to function as a
        client for [`PrivateBin`][privatebin.PrivateBin]. I do test that a few
        HTTP clients statically satisfy this Protocol, but I only run
        PrivateBin's actual client tests against the one I depend on
        (used to be `httpx`, now `httpx2`).

        That's also what motivated writing this Protocol in the first place.
        Switching the client type directly from `httpx.Client` to
        `httpx2.Client` would cause static type errors for anyone still passing
        an `httpx.Client`, even though it provides everything PrivateBin needs
        and continues to work just fine. I can't exactly migrate every project
        I have relying on this library to httpx2 on the same day, and I can't
        expect everyone else to migrate theirs that quickly either, while not
        switching would mean poor Python 3.14+ support.

        So this Protocol is what I came up with to let PrivateBin switch to
        httpx2 without causing superfluous static type errors for clients that
        are already perfectly compatible.
    """

    @property
    def headers(self) -> HeadersProtocol:
        """HTTP headers that support updating."""
        ...

    def get(self, url: str, *, params: str | None = None) -> ResponseProtocol:
        """Send a GET request."""
        ...

    def post(self, url: str, *, json: dict[str, Any]) -> ResponseProtocol:
        """Send a POST request with a JSON body."""
        ...

    def close(self) -> None:
        """Close the HTTP client and release its resources."""
        ...
