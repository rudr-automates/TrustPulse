from datetime import date, datetime
from typing import Any


STATUS_FACTORS = {
    "verified": 1.00,
    "documented": 0.90,
    "self_declared": 0.60,
    "under_review": 0.50,
    "low_quality": 0.40,
    "not_verified": 0.30,
    "unreadable": 0.00,
    "duplicate": 0.00,
    "uploaded": 0.80,
}


AUTHENTICITY_FACTORS = {
    "no_significant_indicators": 1.00,
    "inconclusive": 0.60,
    "potential_manipulation": 0.35,
    "not_assessed": 0.80,
}


CATEGORY_CONFIG = {
    "repayment": {
        "dimension": "repayment_reliability",
        "signal_type": "repayment_activity",
        "base_score": 70,
        "description": "Repayment evidence contributes to the repayment reliability profile.",
    },
    "recurring_payment": {
        "dimension": "payment_discipline",
        "signal_type": "recurring_payment_activity",
        "base_score": 65,
        "description": "Recurring payment evidence contributes to the payment discipline profile.",
    },
    "business": {
        "dimension": "business_continuity",
        "signal_type": "business_activity",
        "base_score": 65,
        "description": "Business evidence contributes to the business continuity profile.",
    },
    "income_sales": {
        "dimension": "income_sales_capacity",
        "signal_type": "income_sales_activity",
        "base_score": 65,
        "description": "Income and sales evidence contributes to the income and sales profile.",
    },
    "tax": {
        "dimension": "income_sales_capacity",
        "signal_type": "tax_support",
        "base_score": 50,
        "description": "Tax evidence provides supporting context for the financial profile.",
    },
    "asset": {
        "dimension": "business_continuity",
        "signal_type": "asset_support",
        "base_score": 40,
        "description": "Asset evidence provides supporting context for continuity.",
    },
    "supporting": {
        "dimension": "business_continuity",
        "signal_type": "supporting_record",
        "base_score": 35,
        "description": "Supporting evidence contributes limited additional context.",
    },
}


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
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


def recency_factor(extracted_date: Any) -> float:
    parsed = parse_date(extracted_date)

    if parsed is None:
        return 0.80

    today = date.today()

    if parsed > today:
        return 0.00

    age_days = (today - parsed).days

    if age_days <= 90:
        return 1.00

    if age_days <= 180:
        return 0.90

    if age_days <= 365:
        return 0.75

    return 0.60


def corroboration_factor(count: int) -> float:
    count = max(0, count)

    return min(
        1.00 + (count * 0.10),
        1.30,
    )


def quality_factor(document_quality: Any) -> float:
    if document_quality is None:
        return 0.85

    try:
        quality = float(document_quality)
    except (TypeError, ValueError):
        return 0.85

    return clamp(quality, 0, 100) / 100


def build_signal(
    evidence: dict,
    extracted_facts: dict,
    validation: dict,
    corroboration_count: int,
) -> dict:
    category = evidence["category"]

    config = CATEGORY_CONFIG.get(category)

    if not config:
        return None

    status = evidence.get("status", "uploaded")

    authenticity_status = validation.get(
        "authenticity_status",
        "not_assessed",
    )

    status_factor = STATUS_FACTORS.get(
        status,
        0.50,
    )

    authenticity_factor = AUTHENTICITY_FACTORS.get(
        authenticity_status,
        0.60,
    )

    contradiction_factor = (
        0.65
        if validation.get("contradiction_detected")
        else 1.00
    )

    quality = quality_factor(
        validation.get("document_quality")
    )

    recency = recency_factor(
        extracted_facts.get("date")
    )

    corroboration = corroboration_factor(
        corroboration_count
    )

    strength_factor = (
        status_factor
        * authenticity_factor
        * quality
        * recency
        * corroboration
        * contradiction_factor
    )

    strength = clamp(
        config["base_score"] * strength_factor
    )

    explanation_parts = [
        config["description"],
        f"Evidence status: {status}.",
        f"Authenticity assessment: {authenticity_status}.",
    ]

    if corroboration_count > 0:
        explanation_parts.append(
            f"{corroboration_count} other evidence item(s) corroborate this record."
        )

    if validation.get("contradiction_detected"):
        explanation_parts.append(
            "Confidence is reduced because validation identified a contradiction or anomaly."
        )

    if not extracted_facts.get("date"):
        explanation_parts.append(
            "Recency could not be fully assessed because no usable date was extracted."
        )

    return {
        "dimension": config["dimension"],
        "signal_type": config["signal_type"],
        "signal_score": round(strength, 2),
        "strength": round(strength_factor * 100, 2),
        "evidence_ids": [evidence["id"]],
        "explanation": " ".join(explanation_parts),
    }