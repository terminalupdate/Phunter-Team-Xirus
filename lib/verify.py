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
    except (OSError, json.JSONDecodeError) as exc:
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


async def check_update(remote_url: str = "https://raw.githubusercontent.com/N0rz3/Phunter/master/config.json") -> dict:
    """Compare local and remote version metadata.

    A transport failure, non-200 status, invalid JSON, or malformed remote
    config is reported as inconclusive, not as an up-to-date installation.
    """
    local_version = version()
    if local_version is None:
        return {"status": "unknown", "local_version": None, "remote_version": None}

    response = await Request(remote_url).get()
    if response is None:
        print(f"[{YELLOW}i{WHITE}] Update check inconclusive: no HTTP response")
        return {"status": "unknown", "local_version": local_version, "remote_version": None}

    # Requests.py represents transport failures with a synthetic HTTP 599.
    if response.status_code == 599 and response.extensions.get("phunter_error"):
        error_type = response.extensions.get("phunter_error")
        print(f"[{YELLOW}i{WHITE}] Update check unavailable: transport error ({error_type})")
        return {"status": "unknown", "local_version": local_version, "remote_version": None}

    if response.status_code != 200:
        print(f"[{YELLOW}i{WHITE}] Update check inconclusive: HTTP {response.status_code}")
        return {"status": "unknown", "local_version": local_version, "remote_version": None}

    try:
        remote_config = response.json()
    except (ValueError, json.JSONDecodeError):
        print(f"[{YELLOW}i{WHITE}] Update check inconclusive: response is not valid JSON")
        return {"status": "unknown", "local_version": local_version, "remote_version": None}

    remote_version = remote_config.get("version") if isinstance(remote_config, dict) else None
    if not isinstance(remote_version, str) or not remote_version.strip():
        print(f"[{YELLOW}i{WHITE}] Update check inconclusive: remote version is missing or invalid")
        return {"status": "unknown", "local_version": local_version, "remote_version": None}

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
    """Check endpoint HTTP reachability, not the site's OSINT functionality.

    ``services`` is injectable so tests can use local/mock endpoints without
    making external network requests. A received 4xx/5xx response still proves
    that an HTTP server answered, but indicates that the endpoint did not
    return a successful response.
    """
    services = tuple(services) if services is not None else DEFAULT_SERVICES
    print(f"\n[{BLUE}INFO{WHITE}] Checking service HTTP reachability...")
    results = []

    for name, url in services:
        try:
            response = await Request(url).get()
        except Exception as exc:  # Defensive boundary for injected/custom clients.
            result = {"name": name, "url": url, "status_code": None,
                      "reachability": "unknown", "http_result": "request_error",
                      "error": type(exc).__name__}
            print(f"  ├── [{YELLOW}UNKNOWN{WHITE}] {name}: request error ({type(exc).__name__})")
            results.append(result)
            continue

        if response is None:
            result = {"name": name, "url": url, "status_code": None,
                      "reachability": "unknown", "http_result": "no_response",
                      "error": None}
            print(f"  ├── [{YELLOW}UNKNOWN{WHITE}] {name}: no response")
        elif response.status_code == 599 and response.extensions.get("phunter_error"):
            error_type = response.extensions.get("phunter_error")
            result = {"name": name, "url": url, "status_code": 599,
                      "reachability": "unreachable", "http_result": "transport_error",
                      "error": error_type}
            print(f"  ├── [{RED}UNREACHABLE{WHITE}] {name}: transport error ({error_type})")
        else:
            code = response.status_code
            if 200 <= code < 300:
                http_result = "success"
                color = GREEN
                label = "HTTP OK"
            elif 300 <= code < 400:
                http_result = "redirect"
                color = YELLOW
                label = "HTTP redirect"
            elif 400 <= code < 500:
                http_result = "client_error"
                color = YELLOW
                label = "HTTP client error"
            else:
                http_result = "server_error"
                color = RED
                label = "HTTP server error"
            result = {"name": name, "url": url, "status_code": code,
                      "reachability": "reachable", "http_result": http_result,
                      "error": None}
            print(f"  ├── [{color}{code}{WHITE}] {name}: {label}; HTTP server reachable")

        results.append(result)

    print("[i] These checks test HTTP reachability only; they do not validate search, reputation, or spam-detection features.")
    return results
