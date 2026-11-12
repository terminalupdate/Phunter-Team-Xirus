"""Best-effort parser for the public Free-Lookup result page.

The page layout is controlled by a third party and may change. Missing or
blocked pages are reported as unavailable, never interpreted as negative data.
"""

from pathlib import Path
from urllib.parse import quote
import random

from bs4 import BeautifulSoup

from .Requests import Request
from .text import BLUE, GREEN, WHITE


PROJECT_ROOT = Path(__file__).resolve().parent.parent
USER_AGENTS_FILE = PROJECT_ROOT / "useragents.txt"


def _load_user_agents():
    try:
        agents = [
            line.strip()
            for line in USER_AGENTS_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return agents or ["Phunter-OSINT/educational"]
    except OSError:
        return ["Phunter-OSINT/educational"]


async def free(phone_number):
    """Retrieve publicly displayed metadata, if the source page is available.

    Returns a dictionary of extracted labels and values. It does not verify
    ownership, current subscriber identity, or the accuracy of page content.
    """
    digits = "".join(ch for ch in str(phone_number) if ch.isdigit())
    if not digits:
        print(f"\n [{BLUE}i{WHITE}] Free-Lookup: invalid input; request skipped")
        return {}

    url = f"https://free-lookup.net/{quote(digits, safe='')}"
    headers = {"user-agent": random.choice(_load_user_agents())}
    response = await Request(url, headers=headers).get()

    if response is None or response.status_code != 200:
        status = getattr(response, "status_code", "no response")
        print(f"\n [{BLUE}i{WHITE}] Free-Lookup unavailable (HTTP {status})")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    summary = soup.find("ul", class_="report-summary__list")
    if summary is None:
        print(f"\n [{BLUE}i{WHITE}] Free-Lookup page structure not recognized; no data extracted")
        return {}

    extracted = {}
    for item in summary.find_all("li"):
        parts = [node.get_text(" ", strip=True) for node in item.find_all("div")]
        parts = [part for part in parts if part]
        if len(parts) >= 2:
            extracted[parts[0]] = parts[1]

    # Compatibility with the original markup, where label/value divs may not
    # be wrapped in individual <li> elements.
    if not extracted:
        parts = [node.get_text(" ", strip=True) for node in summary.find_all("div")]
        parts = [part for part in parts if part]
        for index in range(0, len(parts) - 1, 2):
            extracted[parts[index]] = parts[index + 1]

    print(f"\n [{GREEN}>{WHITE}] Free-Lookup")
    if not extracted:
        print("  └── No recognizable public information found")
        return {}

    for label, value in extracted.items():
        print(f"  ├── {label}: {value}")

    print("  [i] These are source-provided claims, not independently verified facts.")
    return extracted
