"""
Rental scam screening.

Signals are weighted by how *diagnostic* they are, not treated equally. Phrases
that appear constantly in honest ads ("available immediately") barely move the
score; phrases that almost never appear in honest ads ("wire transfer") move it
a lot. Flat scoring produced false positives on legitimate listings, which is
the worst failure mode here — it teaches people to ignore the warning.

The price check compares against the typical asking rent for the listing's own
area when that is known. A fixed dollar threshold cannot tell a normal Maple
Ridge studio from an obviously fake three-bedroom downtown.
"""

from backend.services.price_utils import parse_price

MAX_SCORE = 100

# Rarely present in a legitimate ad. Each is close to decisive on its own.
STRONG_SIGNALS = {
    "wire transfer": "Asks for a wire transfer — untraceable and unrecoverable.",
    "western union": "Asks for Western Union — a hallmark of rental fraud.",
    "money gram": "Asks for MoneyGram — a hallmark of rental fraud.",
    "cash only": "Cash only — legitimate landlords accept traceable payment.",
    "deposit first": "Wants a deposit before you have seen the unit.",
    "no viewing": "No viewing offered before payment.",
    "without viewing": "No viewing offered before payment.",
    "out of the country": "Landlord claims to be out of the country — a common pretext for avoiding a viewing.",
    "overseas": "Landlord claims to be overseas — a common pretext for avoiding a viewing.",
    "keys by mail": "Offers to mail the keys — the unit likely does not exist.",
    "send the deposit": "Pressures you to send a deposit to hold the unit.",
}

# Unusual, but has innocent explanations.
MODERATE_SIGNALS = {
    "no credit check": "No credit check — unusual for a managed building.",
    "no background check": "No background check — unusual for a managed building.",
    "no lease": "No written lease offered. A tenancy agreement protects you.",
    "first come first served": "Manufactured competition to rush your decision.",
}

# Extremely common in honest listings. Present for context, not accusation.
WEAK_SIGNALS = {
    "urgent": "Urgency language.",
    "available immediately": "Urgency language.",
    "act fast": "Urgency language.",
    "before it's gone": "Urgency language.",
    "dm quickly": "Pushes you to move to direct messages quickly.",
}

STRONG_POINTS = 30
MODERATE_POINTS = 12
WEAK_POINTS = 4

# Used only when the listing's area has too little data for a real comparison.
FALLBACK_CHEAP_PRICE = 1200


BEDROOM_WORDS = {0: "studio", 1: "one-bedroom", 2: "two-bedroom", 3: "three-bedroom"}


def _score_price(amount, market_rent, area_label, bedrooms=None):
    """
    Points and reason for the asking price.

    market_rent is CMHC's average rent for the area and unit size — a published
    market figure, so the number quoted back to the reader is one they can
    verify, not something derived from our own sample listings.
    """
    if amount is None:
        return 0, None

    if market_rent:
        ratio = amount / market_rent
        where = f" in {area_label}" if area_label else ""
        size = f"{BEDROOM_WORDS[bedrooms]} " if bedrooms in BEDROOM_WORDS else ""

        # CMHC's average covers the whole existing stock, including long-term
        # tenants on old rents, so a newly advertised unit normally asks *more*
        # than this figure. Sitting well under it is therefore a stronger
        # signal than the raw ratio suggests, and the bands reflect that.
        if ratio < 0.7:
            return 40, (
                f"${amount:,} is far below the going rate — CMHC puts the "
                f"average {size}rent{where} at ${market_rent:,}, and newly "
                "advertised units usually ask more than that, not less."
            )
        if ratio < 0.85:
            return 20, (
                f"${amount:,} is below the average {size}rent{where} "
                f"(${market_rent:,}, per CMHC)."
            )
        return 0, None

    if amount < FALLBACK_CHEAP_PRICE:
        return 40, (
            f"${amount:,} is unusually low for Metro Vancouver."
        )

    return 0, None


def analyze_listing(title, price, market_rent=None, area_label=None,
                    bedrooms=None):
    """
    Screen a listing for scam indicators.

    market_rent: CMHC average rent for the area and unit size, if known.
    Enables a market-relative price check instead of a fixed threshold.
    """
    score = 0
    reasons = []

    text = (title or "").lower()

    price_points, price_reason = _score_price(
        parse_price(price), market_rent, area_label, bedrooms
    )
    score += price_points
    if price_reason:
        reasons.append(price_reason)

    for signals, points in (
        (STRONG_SIGNALS, STRONG_POINTS),
        (MODERATE_SIGNALS, MODERATE_POINTS),
        (WEAK_SIGNALS, WEAK_POINTS),
    ):
        seen = set()
        for phrase, explanation in signals.items():
            # Several phrases share one explanation; don't repeat it.
            if phrase in text and explanation not in seen:
                seen.add(explanation)
                score += points
                reasons.append(explanation)

    score = min(score, MAX_SCORE)

    if score >= 60:
        risk_level = "HIGH"
    elif score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
    }
