"""Conservative SpamCalls page parser.

A successful HTTP response is not a spam verdict. This module only reports a
positive or negative result when the returned page contains an explicit,
recognizable statement. Otherwise the result is ``unknown``.
"""

from __future__ import annotations

import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from .Requests import Request
from .text import BLUE, GREEN, RED, WHITE, YELLOW


# Deliberately narrow patterns to reduce false positives from generic site
# navigation, advertisements, or the word "spam" in the site's branding.
_REPORTED_PATTERNS = (
    re.compile(r"\b(?:this|the)\s+(?:phone\s+)?number\s+(?:is\s+)?(?:reported|marked|flagged|identified)\s+as\s+(?:spam|scam|fraud)\b", re.I),
    re.compile(r"\b(?:this|the)\s+(?:phone\s+)?number\s+(?:is\s+)?a\s+(?:spam|scam|fraudulent)\s+(?:number|caller)\b", re.I),
    re.compile(r"\b(?:users|callers)\s+(?:have\s+)?reported\s+(?:this\s+)?(?:number|caller)\s+as\s+(?:spam|scam|fraud)\b", re.I),
)
_NOT_REPORTED_PATTERNS = (
    re.compile(r"\bno\s+(?:spam\s+)?reports?\s+(?:for|about|on)\s+(?:this\s+)?(?:number|phone number)\b", re.I),
    re.compile(r"\b(?:this\s+)?(?:number|phone number)\s+(?:has\s+)?not\s+been\s+reported\b", re.I),
    re.compile(r"\bno\s+user\s+reports?\b", re.I),
    re.compile(r"\bno\s+complaints?\s+(?:for|about|on)\s+(?:this\s+)?(?:number|phone number)\b", re.I),
)


def _page_text(html: str) -> str:
    """Extract likely page content, avoiding scripts/styles/navigation first."""
    soup = BeautifulSoup(html or "", "html.parser")
    for node in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
        node.decompose()

    main = soup.find("main") or soup.find("article") or soup.find(id=re.compile(r"content|main", re.I))
    root = main if main is not None else soup.body or soup
    return " ".join(root.stripped_strings)


def _classify(text: str) -> tuple[str, str | None]:
    """Return (reported|not_reported|unknown, matching evidence)."""
    # Explicit negative statements take precedence over broad category words.
    for pattern in _NOT_REPORTED_PATTERNS:
        match = pattern.search(text)
        if match:
            return "not_reported", match.group(0)

    for pattern in _REPORTED_PATTERNS:
        match = pattern.search(text)
        if match:
            return "reported", match.group(0)

    return "unknown", None


async def spamcalls(p_n):
    """Check the public SpamCalls page and return a tri-state result.

    ``not_reported`` means only that the source explicitly displayed a
    no-report statement; it does not prove that the number is safe.
    """
    raw = str(p_n).strip()
    digits = "".join(character for character in raw if character.isdigit())
    if not digits:
        result = {"status": "unknown", "source": "SpamCalls", "evidence": None, "reason": "invalid phone number"}
        print(f"\n [{YELLOW}i{WHITE}] SpamCalls: invalid number; check skipped")
        return result

    url = f"https://spamcalls.net/en/number/{quote(digits, safe='')}"
    response = await Request(url).get()

    if response is None or response.status_code != 200:
        status_code = getattr(response, "status_code", None)
        reason = f"HTTP {status_code}" if status_code is not None else "no response"
        result = {"status": "unknown", "source": "SpamCalls", "evidence": None, "reason": reason}
        print(f"\n [{YELLOW}i{WHITE}] SpamCalls: result unavailable ({reason})")
        return result

    text = _page_text(response.text)
    status, evidence = _classify(text)

    if status == "reported":
        print(f"\n [{RED}!{WHITE}] SpamCalls: source reports a spam/scam-related classification")
    elif status == "not_reported":
        print(f"\n [{GREEN}>{WHITE}] SpamCalls: source explicitly reports no complaints")
        print("  [i] This does not prove that the number is safe.")
    else:
        print(f"\n [{YELLOW}i{WHITE}] SpamCalls: no explicit, recognizable verdict found")

    if evidence:
        print(f"  └── Source text: {evidence}")
    else:
        print("  └── Status: unknown (page availability is not a spam verdict)")

    return {
        "status": status,
        "source": "SpamCalls",
        "evidence": evidence,
        "reason": None if evidence else "no explicit verdict recognized",
    }
