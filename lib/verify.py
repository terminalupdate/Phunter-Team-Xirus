"""Local version and third-party endpoint checks for Phunter.

The checks in this module distinguish HTTP reachability from the correctness
or availability of a site's OSINT functionality. No phone-number lookups are
performed here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from .Requests import Request
from .text import BLUE, GREEN, RED, WHITE, YELLOW


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"

DEFAULT_SERVICES = (
    ("Free-Lookup", "https://free-lookup.net"),
    ("Tellows", "https://www.tellows.fr"),
    ("SpamCalls", "https://spamcalls.net/en"),
)


def _read_local_version() -> Optional[str]:
    """Read the installed version independently of the current directory."""
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"[{RED}!{WHITE}] Cannot read local config: {exc}")
        return None

    version_value = config.get("version") if isinstance(config, dict) else None
    if not isinstance(version_value, str) or not version_value.strip():
        print(f"[{RED}!{WHITE}] Local config does not contain a valid version")
        return None
    return version_value.strip()


def version() -> Optional[str]:
    """Print and return the locally installed Phunter version."""
    current = _read_local_version()
    if current is not None:
        print(f"[{BLUE}INFO{WHITE}] Your version is: {current}")
    return current


def _transport_error(response) -> Optional[str]:
    """Return the transport exception marker used by ``Request``, if present.

    HTTP status 599 alone is not enough to prove a transport failure: a real
    server could theoretically return that non-standard status. The marker is
    what distinguishes Phunter's synthetic response from a real HTTP reply.
    """
    extensions = getattr(response, "extensions", None) or {}
    error = extensions.get("phunter_error") if hasattr(extensions, "get") else None
    if getattr(response, "status_code", None) == 599 and error:
        return str(error)
    return None


def _unknown_update(local_version: Optional[str], message: str) -> dict:
    """Build a consistent inconclusive update-check result."""
    print(f"[{YELLOW}i{WHITE}] Update check inconclusive: {message}")
    return {
        "status": "unknown",
        "local_version": local_version,
        "remote_version": None,
    }


async def check_update(
    remote_url: str = "https://raw.githubusercontent.com/N0rz3/Phunter/master/config.json",
) -> dict:
    """Compare local and remote version metadata without false success states.

    Transport errors, timeouts, non-200 responses, invalid JSON and malformed
    remote metadata are all reported as ``unknown`` rather than as
    ``up_to_date``. ``remote_url`` is injectable to keep tests fully local.
    """
    local_version = version()
    if local_version is None:
        return {"status": "unknown", "local_version": None, "remote_version": None}

    try:
        response = await Request(remote_url).get()
    except Exception as exc:  # Defensive boundary for custom clients/test doubles.
        return _unknown_update(local_version, f"request error ({type(exc).__name__})")

    if response is None:
        return _unknown_update(local_version, "no HTTP response")

    transport_error = _transport_error(response)
    if transport_error:
        return _unknown_update(local_version, f"transport error ({transport_error})")

    status_code = getattr(response, "status_code", None)
    if status_code != 200:
        return _unknown_update(local_version, f"HTTP {status_code}")

    try:
        remote_config = response.json()
    except (ValueError, UnicodeError):
        return _unknown_update(local_version, "response is not valid JSON")

    remote_version = (
        remote_config.get("version") if isinstance(remote_config, dict) else None
    )
    if not isinstance(remote_version, str) or not remote_version.strip():
        return _unknown_update(local_version, "remote version is missing or invalid")

    remote_version = remote_version.strip()
    if local_version != remote_version:
        print(f"[{RED}-{WHITE}] Your version differs from the repository version ({remote_version})")
        print(f"[{BLUE}INFO{WHITE}] Review the changes before updating: https://github.com/N0rz3/Phunter")
        status = "update_available"
    else:
        print(f"[{GREEN}>{WHITE}] Your version matches the repository version")
        status = "up_to_date"

    return {
        "status": status,
        "local_version": local_version,
        "remote_version": remote_version,
    }


async def test_url(services: Optional[Iterable[tuple[str, str]]] = None) -> list[dict]:
    """Check HTTP reachability only; do not infer feature functionality.

    ``services`` is injectable so tests can use simulated responses without
    making external network requests. A real 3xx/4xx/5xx response proves that
    an HTTP server answered, even though the requested endpoint did not return
    a normal 2xx success. Every result explicitly marks application features
    as ``not_checked``.
    """
    services = tuple(services) if services is not None else DEFAULT_SERVICES
    print(f"\n[{BLUE}INFO{WHITE}] Checking service HTTP reachability...")
    results = []

    for name, url in services:
        try:
            response = await Request(url).get()
        except Exception as exc:  # Defensive boundary for injected/custom clients.
            result = {
                "name": name,
                "url": url,
                "status_code": None,
                "reachability": "unknown",
                "http_result": "request_error",
                "functionality": "not_checked",
                "error": type(exc).__name__,
            }
            print(f"  ├── [{YELLOW}UNKNOWN{WHITE}] {name}: request error ({type(exc).__name__})")
            results.append(result)
            continue

        if response is None:
            result = {
                "name": name,
                "url": url,
                "status_code": None,
                "reachability": "unknown",
                "http_result": "no_response",
                "functionality": "not_checked",
                "error": None,
            }
            print(f"  ├── [{YELLOW}UNKNOWN{WHITE}] {name}: no response")
        else:
            transport_error = _transport_error(response)
            if transport_error:
                result = {
                    "name": name,
                    "url": url,
                    "status_code": 599,
                    "reachability": "unreachable",
                    "http_result": "transport_error",
                    "functionality": "not_checked",
                    "error": transport_error,
                }
                print(f"  ├── [{RED}UNREACHABLE{WHITE}] {name}: transport error ({transport_error})")
            else:
                code = getattr(response, "status_code", None)
                if not isinstance(code, int):
                    result = {
                        "name": name,
                        "url": url,
                        "status_code": None,
                        "reachability": "unknown",
                        "http_result": "invalid_response",
                        "functionality": "not_checked",
                        "error": "missing or invalid HTTP status code",
                    }
                    print(f"  ├── [{YELLOW}UNKNOWN{WHITE}] {name}: invalid HTTP response")
                else:
                    if 200 <= code < 300:
                        http_result, color, label = "success", GREEN, "HTTP OK"
                    elif 300 <= code < 400:
                        http_result, color, label = "redirect", YELLOW, "HTTP redirect"
                    elif 400 <= code < 500:
                        http_result, color, label = "client_error", YELLOW, "HTTP client error"
                    elif 500 <= code < 600:
                        http_result, color, label = "server_error", RED, "HTTP server error"
                    else:
                        http_result, color, label = "other", YELLOW, "HTTP response"

                    result = {
                        "name": name,
                        "url": url,
                        "status_code": code,
                        "reachability": "reachable",
                        "http_result": http_result,
                        "functionality": "not_checked",
                        "error": None,
                    }
                    print(f"  ├── [{color}{code}{WHITE}] {name}: {label}; HTTP server reachable")

        results.append(result)

    print(
        "[i] These checks test HTTP reachability only; search, reputation, "
        "and spam-detection functionality is not tested."
    )
    return results
