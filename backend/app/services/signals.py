from datetime import date, datetime
from typing import Any


CATEGORY_CONFIG = {
    "repayment": {
        "dimension": "repayment_reliability",
        "signal_type": "repayment_activity",
        "base_score": 75.0,
        "description": (
            "Repayment evidence contributes to repayment reliability."
        ),
    },
    "recurring_payment": {
        "dimension": "payment_discipline",
        "signal_type": "recurring_payment_activity",
        "base_score": 72.0,
        "description": (
            "Recurring payment evidence contributes to payment discipline."
        ),
    },
    "business": {
        "dimension": "business_continuity",
        "signal_type": "business_activity",
        "base_score": 72.0,
        "description": (
            "Business evidence contributes to business continuity."
        ),
    },
    "income_sales": {
        "dimension": "income_sales_capacity",
        "signal_type": "income_sales_activity",
        "base_score": 68.0,
        "description": (
            "Income and sales evidence contributes to income and sales capacity."
        ),
    },
    "tax": {
        "dimension": "income_sales_capacity",
        "signal_type": "tax_support",
        "base_score": 60.0,
        "description": (
            "Tax evidence provides supporting context for financial capacity."
        ),
    },
    "asset": {
        "dimension": "business_continuity",
        "signal_type": "asset_support",
        "base_score": 58.0,
        "description": (
            "Asset evidence provides supporting context for continuity."
        ),
    },
    "supporting": {
        "dimension": "business_continuity",
        "signal_type": "supporting_record",
        "base_score": 50.0,
        "description": (
            "Supporting evidence contributes additional financial context."
        ),
    },
}


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(minimum, min(maximum, value))


def parse_date(value: Any) -> date | None:
    if not value or not isinstance(value, str):
        return None

    value = value.strip()

    formats = [
        "%Y-%m-%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def recency_factor(
    extracted_date: Any,
) -> float:
    parsed = parse_date(extracted_date)

    if parsed is None:
        return 0.90

    today = date.today()

    if parsed > today:
        return 0.00

    age_days = (today - parsed).days

    if age_days <= 90:
        return 1.00

    if age_days <= 180:
        return 0.97

    if age_days <= 365:
        return 0.92

    return 0.85


def behavioral_adjustment(
    category: str,
    extracted_facts: dict,
) -> float:
    """
    Adjust the underlying financial-behavior signal based only on
    observable financial behavior extracted from the evidence.

    Evidence quality, authenticity, contradictions, and corroboration
    are intentionally excluded from this function. Those belong to
    the Confidence layer.
    """

    adjustment = 0.0

    if category == "repayment":
        repayment_details = (
            extracted_facts.get("repayment_details")
            or {}
        )

        payment_status = str(
            repayment_details.get(
                "payment_status",
                "",
            )
        ).lower()

        if "on time" in payment_status:
            adjustment += 8.0

        if "late" in payment_status:
            adjustment -= 8.0

        if "missed" in payment_status:
            adjustment -= 15.0

        if "paid" in payment_status:
            adjustment += 4.0

    elif category == "recurring_payment":
        payment_details = (
            extracted_facts.get("payment_details")
            or {}
        )

        payment_status = str(
            payment_details.get(
                "status",
                payment_details.get(
                    "payment_status",
                    "",
                ),
            )
        ).lower()

        if "paid" in payment_status:
            adjustment += 4.0

        if "late" in payment_status:
            adjustment -= 5.0

    elif category == "business":
        business_details = (
            extracted_facts.get("business_details")
            or {}
        )

        if business_details:
            adjustment += 3.0

    elif category == "income_sales":
        income_details = (
            extracted_facts.get("income_details")
            or {}
        )

        if income_details:
            adjustment += 3.0

    return adjustment


def build_signal(
    evidence: dict,
    extracted_facts: dict,
    validation: dict,
    corroboration_count: int,
) -> dict | None:
    category = evidence["category"]

    config = CATEGORY_CONFIG.get(category)

    if not config:
        return None

    base_score = config["base_score"]

    behavior_adjustment = behavioral_adjustment(
        category=category,
        extracted_facts=extracted_facts,
    )

    recency = recency_factor(
        extracted_facts.get("date")
    )

    # Recency affects the observed strength of the financial behavior,
    # but does not create a catastrophic penalty.
    signal_score = (
        base_score + behavior_adjustment
    ) * recency

    signal_score = clamp(signal_score)

    # "Strength" describes evidence support for this signal.
    # It is intentionally separate from the behavioral score.
    strength = 100.0

    if validation.get("authenticity_status") == "inconclusive":
        strength -= 20.0

    if validation.get("authenticity_status") == "potential_manipulation":
        strength -= 40.0

    if validation.get("contradiction_detected"):
        strength -= 25.0

    if validation.get("missing_fields"):
        missing_count = len(
            validation["missing_fields"]
        )

        strength -= min(
            missing_count * 5.0,
            20.0,
        )

    strength += min(
        corroboration_count * 5.0,
        15.0,
    )

    strength = clamp(strength)

    explanation_parts = [
        config["description"],
        f"Observed behavioral signal: {round(signal_score, 2)}/100.",
    ]

    if behavior_adjustment > 0:
        explanation_parts.append(
            "Extracted financial behavior provided positive signal support."
        )
    elif behavior_adjustment < 0:
        explanation_parts.append(
            "Extracted financial behavior provided negative signal support."
        )

    if recency < 1.0:
        explanation_parts.append(
            "Older evidence carries slightly less current weight."
        )

    if corroboration_count > 0:
        explanation_parts.append(
            f"{corroboration_count} other evidence item(s) "
            "provide corroborating support."
        )

    if validation.get("contradiction_detected"):
        explanation_parts.append(
            "Evidence quality or consistency issues reduce confidence "
            "in this signal."
        )

    return {
        "dimension": config["dimension"],
        "signal_type": config["signal_type"],
        "signal_score": round(signal_score, 2),
        "strength": round(strength, 2),
        "evidence_ids": [evidence["id"]],
        "explanation": " ".join(explanation_parts),
    }