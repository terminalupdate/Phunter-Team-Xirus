"""Phone-number parsing and reporting for Phunter.

This module validates and normalizes a number before querying optional
third-party reputation/search services. It does not identify the subscriber.
"""

import phonenumbers
from phonenumbers import carrier, geocoder
from phonenumbers.phonenumberutil import NumberParseException

from .reputation import reputation
from .free_lookup import free
from .spam import spamcalls
from .text import BLUE, GREEN, RED, WHITE


def _line_type(number_type):
    """Return a readable libphonenumber line type."""
    labels = {
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed line",
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed line or mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll-free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium-rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Shared-cost",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal number",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "Universal access number",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
    }
    return labels.get(number_type, "Unknown")


async def lookup(phone_number, region=None):
    """Analyze an international number (preferably E.164, e.g. +393...).

    `region` is an optional ISO 3166-1 alpha-2 region such as "IT". It is
    needed only when the input is national-format rather than international.
    """
    raw_number = str(phone_number).strip()
    if not raw_number:
        print(f" [{RED}!{WHITE}] Empty phone number")
        return

    try:
        parsed = phonenumbers.parse(raw_number, region)
    except NumberParseException as exc:
        print(f" [{RED}!{WHITE}] Cannot parse phone number: {exc}")
        print(" [i] Use international format, for example: +393331234567")
        return

    possible = phonenumbers.is_possible_number(parsed)
    valid = phonenumbers.is_valid_number(parsed)
    e164_number = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.E164
    )
    region_code = phonenumbers.region_code_for_number(parsed)
    country = geocoder.description_for_number(parsed, "it") or "Not available"
    operator = carrier.name_for_number(parsed, "it") or "Not available"
    line_type = _line_type(phonenumbers.number_type(parsed))

    print()
    print(f"{WHITE}📞 Phone number: {BLUE}{e164_number}{WHITE}")
    print(f" [{GREEN}>{WHITE}] Possible: {'✔️' if possible else '❌'}")
    print(f" [{GREEN}>{WHITE}] Valid according to numbering metadata: {'✔️' if valid else '❌'}")
    print(f" [{GREEN}>{WHITE}] Country/region: {country} ({region_code or 'unknown'})")
    print(f" [{GREEN}>{WHITE}] Number type: {line_type}")
    print(f" [{GREEN}>{WHITE}] Carrier metadata: {operator}")

    print(
        " [i] Carrier and geographic descriptions are metadata-based; "
        "they do not prove the current operator, physical location, or identity "
        "of the person using the number."
    )

    # Do not send malformed or metadata-invalid numbers to external services.
    if not possible or not valid:
        print(f" [{RED}!{WHITE}] External lookups skipped because the number did not pass validation.")
        return

    # Existing lookup modules build their URLs from digits without a leading plus sign.
    digits = e164_number.lstrip("+")

    await reputation(digits)
    await free(digits)

    await spamcalls(digits)
