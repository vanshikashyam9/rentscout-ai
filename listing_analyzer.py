# -----------------------------------
# RENTAL SCAM DETECTOR
# -----------------------------------

def analyze_listing(title, price):

    risk_score = 0
    reasons = []

    # -----------------------------------
    # PRICE CHECK
    # -----------------------------------

    try:

        clean_price = (
            price.replace("$", "")
            .replace(",", "")
            .strip()
        )

        clean_price = int(clean_price)

        if clean_price < 1200:

            risk_score += 40

            reasons.append(
                "Price unusually low for Metro Vancouver."
            )

    except:
        pass

    # -----------------------------------
    # SUSPICIOUS WORDS
    # -----------------------------------

    suspicious_words = [
        "deposit first",
        "dm quickly",
        "urgent",
        "before it's gone",
        "available immediately",
        "cash only",
        "no credit check"
    ]

    combined_text = (
        title.lower()
    )

    for word in suspicious_words:

        if word in combined_text:

            risk_score += 15

            reasons.append(
                f"Suspicious phrase: '{word}'"
            )

    # -----------------------------------
    # RISK LEVEL
    # -----------------------------------

    if risk_score >= 60:
        risk_level = "HIGH"

    elif risk_score >= 30:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons
    }