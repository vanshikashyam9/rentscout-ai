"""Shared price parsing so every endpoint handles messy strings the same way."""

import re
from typing import Optional


def parse_price(raw) -> Optional[int]:
    """
    Turn a raw Craigslist price like '$1,800', '$1800/mo', or 'Call'
    into an integer number of dollars, or None if no valid price is found.

    Returning None (never crashing) lets callers skip bad rows cleanly.
    """
    if raw is None:
        return None

    text = str(raw)

    # Grab the first run of digits (with optional commas), ignore the rest.
    match = re.search(r"\d[\d,]*", text)
    if not match:
        return None

    digits = match.group(0).replace(",", "")

    try:
        value = int(digits)
    except ValueError:
        return None

    # Guard against absurd values (e.g. a phone number scraped as price).
    if value <= 0 or value > 100000:
        return None

    return value
