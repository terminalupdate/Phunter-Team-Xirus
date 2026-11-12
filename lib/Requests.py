"""Small, defensive asynchronous HTTP client used by Phunter.

The public API remains compatible with the original code:
    response = await Request(url, headers=..., params=...).get()

Transport failures are represented by an HTTPX response with status 599, so
legacy callers that inspect ``response.status_code`` do not crash. The
original exception class is available in ``response.extensions`` under
``phunter_error``. A 599 response is synthetic and was not returned by the
remote server.
"""

from __future__ import annotations

from typing import Mapping, Optional, Any
from urllib.parse import urlsplit

import httpx


DEFAULT_TIMEOUT = httpx.Timeout(connect=8.0, read=15.0, write=10.0, pool=5.0)
DEFAULT_LIMITS = httpx.Limits(max_connections=10, max_keepalive_connections=5)


class Request:
    """Perform bounded asynchronous HTTP GET requests.

    Args:
        url: Absolute HTTP or HTTPS URL.
        headers: Optional request headers.
        params: Optional query parameters.
        timeout: Timeout in seconds or an ``httpx.Timeout`` instance.
        follow_redirects: Whether to follow HTTP redirects.
        max_redirects: Maximum number of redirects when enabled.
        client: Optional externally-managed AsyncClient, useful for tests or
            callers that want connection pooling. The caller owns its lifetime.
    """

    def __init__(
        self,
        url: str,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        follow_redirects: bool = True,
        max_redirects: int = 5,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.url = str(url)
        self.head = dict(headers or {})
        self.params = params
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.client = client

    def _validate_url(self) -> None:
        parsed = urlsplit(self.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL must be an absolute HTTP or HTTPS URL")

    @staticmethod
    def _failure_response(url: str, error: Exception) -> httpx.Response:
        """Return a clearly synthetic response for backward compatibility."""
        request = httpx.Request("GET", "https://invalid.local/")
        return httpx.Response(
            status_code=599,
            request=request,
            text="Phunter transport error; no HTTP response was received.",
            extensions={"phunter_error": type(error).__name__},
        )

    async def get(self) -> httpx.Response:
        """Send GET and return the HTTP response, or synthetic status 599."""
        try:
            self._validate_url()
            if self.client is not None:
                return await self.client.get(
                    self.url,
                    headers=self.head,
                    params=self.params,
                    timeout=self.timeout,
                    follow_redirects=self.follow_redirects,
                )

            async with httpx.AsyncClient(
                timeout=self.timeout,
                limits=DEFAULT_LIMITS,
                follow_redirects=self.follow_redirects,
                max_redirects=self.max_redirects,
                headers={"User-Agent": "Phunter-OSINT/0.0.3"},
            ) as client:
                return await client.get(
                    self.url,
                    headers=self.head,
                    params=self.params,
                )

        except (httpx.HTTPError, httpx.InvalidURL, ValueError) as exc:
            return self._failure_response(self.url, exc)
