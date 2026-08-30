from collections import defaultdict
from itertools import combinations


def normalize(value: str | None) -> str:
    if not value:
        return ""

    return " ".join(value.lower().split())


def names_match(
    first: str | None,
    second: str | None,
) -> bool:
    if not first or not second:
        return False

    first_tokens = set(normalize(first).split())
    second_tokens = set(normalize(second).split())

    if not first_tokens or not second_tokens:
        return False

    overlap = first_tokens.intersection(second_tokens)

    return len(overlap) >= max(
        1,
        min(len(first_tokens), len(second_tokens)),
    )


def dates_match(
    first: str | None,
    second: str | None,
) -> bool:
    if not first or not second:
        return False

    return first[:7] == second[:7]


def amounts_match(
    first: float | None,
    second: float | None,
) -> bool:
    if first is None or second is None:
        return False

    tolerance = max(
        1.0,
        min(abs(first), abs(second)) * 0.05,
    )

    return abs(first - second) <= tolerance


def compare_evidence(
    first: dict,
    second: dict,
) -> dict:
    first_facts = first.get("extracted_data") or {}
    second_facts = second.get("extracted_data") or {}

    name_match = names_match(
        first_facts.get("name"),
        second_facts.get("name"),
    )

    date_match = dates_match(
        first_facts.get("date"),
        second_facts.get("date"),
    )

    amount_match = amounts_match(
        first_facts.get("amount"),
        second_facts.get("amount"),
    )

    supporting_signals = sum(
        [
            name_match,
            date_match,
            amount_match,
        ]
    )

    if supporting_signals >= 2:
        relation_type = "corroborates"
    elif (
        first_facts.get("name")
        and second_facts.get("name")
        and not name_match
    ):
        relation_type = "contradicts"
    else:
        relation_type = "related"

    explanation_parts: list[str] = []

    if name_match:
        explanation_parts.append(
            "The extracted names are consistent."
        )

    if date_match:
        explanation_parts.append(
            "The evidence refers to the same month."
        )

    if amount_match:
        explanation_parts.append(
            "The extracted amounts are similar."
        )

    if not explanation_parts:
        explanation_parts.append(
            "The evidence items are related but do not provide enough matching information to establish corroboration."
        )

    return {
        "relation_type": relation_type,
        "explanation": " ".join(explanation_parts),
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
                "source_evidence_id": first["evidence_id"],
                "target_evidence_id": second["evidence_id"],
                **comparison,
            }
        )

    return relationships


def count_corroboration(
    relationships: list[dict],
) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)

    for relationship in relationships:
        if relationship["relation_type"] == "corroborates":
            counts[
                relationship["source_evidence_id"]
            ] += 1

            counts[
                relationship["target_evidence_id"]
            ] += 1

    return dict(counts)