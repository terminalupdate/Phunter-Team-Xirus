"""Best-effort extraction of a Tellows public number reputation page."""

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


async def reputation(phone_number):
    """Extract the displayed Tellows heading, if available.

    A page response is not proof that a number is safe or dangerous. The
    function reports source availability and visible text only.
    """
    digits = "".join(ch for ch in str(phone_number) if ch.isdigit())
    if not digits:
        print(f"\n [{BLUE}i{WHITE}] Tellows: invalid input; request skipped")
        return None

    encoded_number = quote(f"+{digits}", safe="")
    url = f"https://www.tellows.fr/num/{encoded_number}"
    headers = {"user-agent": random.choice(_load_user_agents())}
    response = await Request(url=url, headers=headers).get()

    if response is None or response.status_code != 200:
        status = getattr(response, "status_code", "no response")
        print(f"\n [{BLUE}i{WHITE}] Tellows unavailable (HTTP {status})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    candidates = soup.select(".col-lg-9 h1, main h1, h1")
    heading = next(
        (node.get_text(" ", strip=True) for node in candidates if node.get_text(strip=True)),
        None,
    )

    if not heading:
        print(f"\n [{BLUE}i{WHITE}] Tellows: no recognizable reputation heading found")
        return None

    print(f"\n [{GREEN}>{WHITE}] Tellows page: {heading}")
    print("  [i] Page text is a community/source indicator, not a verified verdict.")
    return heading
