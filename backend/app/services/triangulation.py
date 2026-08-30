from collections import defaultdict
from datetime import date, datetime
from itertools import combinations


BUSINESS_CATEGORIES = {
    "business",
    "income_sales",
    "tax",
    "asset",
}

PAYMENT_CATEGORIES = {
    "repayment",
    "recurring_payment",
}


def normalize(value: str | None) -> str:
    if not value:
        return ""

    return " ".join(value.lower().split())


def tokenize(value: str | None) -> set[str]:
    normalized = normalize(value)

    if not normalized:
        return set()

    return set(normalized.split())


def names_match(
    first: str | None,
    second: str | None,
) -> bool:
    if not first or not second:
        return False

    first_tokens = tokenize(first)
    second_tokens = tokenize(second)

    if not first_tokens or not second_tokens:
        return False

    overlap = first_tokens.intersection(
        second_tokens
    )

    return len(overlap) >= 1


def parse_date(
    value: str | None,
) -> date | None:
    if not value:
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
            return datetime.strptime(
                value,
                fmt,
            ).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(
            value
        ).date()
    except ValueError:
        return None


def dates_are_close(
    first: str | None,
    second: str | None,
    max_days: int = 90,
) -> bool:
    first_date = parse_date(first)
    second_date = parse_date(second)

    if not first_date or not second_date:
        return False

    difference = abs(
        (first_date - second_date).days
    )

    return difference <= max_days


def amounts_match(
    first: float | None,
    second: float | None,
) -> bool:
    if first is None or second is None:
        return False

    tolerance = max(
        1.0,
        min(
            abs(first),
            abs(second),
        ) * 0.05,
    )

    return abs(first - second) <= tolerance


def complementary_categories(
    first: str,
    second: str,
) -> bool:
    if first == second:
        return False

    if (
        first in BUSINESS_CATEGORIES
        and second in BUSINESS_CATEGORIES
    ):
        return True

    if (
        first in BUSINESS_CATEGORIES
        and second in PAYMENT_CATEGORIES
    ):
        return True

    if (
        first in PAYMENT_CATEGORIES
        and second in BUSINESS_CATEGORIES
    ):
        return True

    return True


def business_context_matches(
    first_facts: dict,
    second_facts: dict,
) -> bool:
    first_business = (
        first_facts.get("business_details")
        or {}
    )

    second_business = (
        second_facts.get("business_details")
        or {}
    )

    first_business_name = first_business.get(
        "business_name"
    )

    second_business_name = second_business.get(
        "business_name"
    )

    if first_business_name and second_business_name:
        first_tokens = tokenize(
            str(first_business_name)
        )

        second_tokens = tokenize(
            str(second_business_name)
        )

        if first_tokens.intersection(
            second_tokens
        ):
            return True

    first_location = (
        first_business.get("business_location")
        or first_business.get("location")
    )

    second_location = (
        second_business.get("business_location")
        or second_business.get("location")
    )

    if first_location and second_location:
        first_location_tokens = tokenize(
            str(first_location)
        )

        second_location_tokens = tokenize(
            str(second_location)
        )

        if first_location_tokens.intersection(
            second_location_tokens
        ):
            return True

    return False


def compare_evidence(
    first: dict,
    second: dict,
) -> dict:
    first_facts = (
        first.get("extracted_data")
        or {}
    )

    second_facts = (
        second.get("extracted_data")
        or {}
    )

    first_category = first.get(
        "category",
        "supporting",
    )

    second_category = second.get(
        "category",
        "supporting",
    )

    identity_match = names_match(
        first_facts.get("name"),
        second_facts.get("name"),
    )

    temporal_match = dates_are_close(
        first_facts.get("date"),
        second_facts.get("date"),
    )

    amount_match = amounts_match(
        first_facts.get("amount"),
        second_facts.get("amount"),
    )

    category_match = complementary_categories(
        first_category,
        second_category,
    )

    business_match = business_context_matches(
        first_facts,
        second_facts,
    )

    supporting_signals = 0
    explanation_parts: list[str] = []

    if identity_match:
        supporting_signals += 1
        explanation_parts.append(
            "The extracted borrower names are consistent."
        )

    if temporal_match:
        supporting_signals += 1
        explanation_parts.append(
            "The evidence refers to activity within the same 90-day period."
        )

    if category_match:
        supporting_signals += 1

    if business_match:
        supporting_signals += 1
        explanation_parts.append(
            "The extracted business context is consistent."
        )

    if amount_match:
        supporting_signals += 1
        explanation_parts.append(
            "The extracted amounts are similar."
        )

    # ---------------------------------------------------------
    # Corroboration requires meaningful evidence support.
    #
    # Two complementary records supporting the same borrower
    # within a relevant time window are enough even when their
    # amounts are naturally different.
    # ---------------------------------------------------------

    if (
        identity_match
        and temporal_match
        and category_match
    ):
        relation_type = "corroborates"

    elif (
        identity_match
        and business_match
    ):
        relation_type = "corroborates"

    elif (
        first_facts.get("name")
        and second_facts.get("name")
        and not identity_match
    ):
        relation_type = "contradicts"

    else:
        relation_type = "related"

    if not explanation_parts:
        explanation_parts.append(
            "The evidence items are related but do not provide enough independent support to establish corroboration."
        )

    if relation_type == "corroborates":
        explanation_parts.append(
            "These records provide complementary support for the borrower's financial activity."
        )

    return {
        "relation_type": relation_type,
        "explanation": " ".join(
            explanation_parts
        ),
        "supporting_signals": supporting_signals,
    }


def build_triangulation(
    evidence_items: list[dict],
) -> list[dict]:
    relationships: list[dict] = []

    for first, second in combinations(
        evidence_items,
        2,
    ):
        comparison = compare_evidence(
            first,
            second,
        )

        relationships.append(
            {
                "source_evidence_id": first[
                    "evidence_id"
                ],
                "target_evidence_id": second[
                    "evidence_id"
                ],
                **comparison,
            }
        )

    return relationships


def count_corroboration(
    relationships: list[dict],
) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)

    for relationship in relationships:
        if relationship["relation_type"] != "corroborates":
            continue

        source_id = relationship[
            "source_evidence_id"
        ]

        target_id = relationship[
            "target_evidence_id"
        ]

        counts[source_id] += 1
        counts[target_id] += 1

    return dict(counts)