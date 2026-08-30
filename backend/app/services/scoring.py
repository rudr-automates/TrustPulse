from collections import defaultdict


DIMENSION_WEIGHTS = {
    "repayment_reliability": 0.30,
    "payment_discipline": 0.25,
    "business_continuity": 0.25,
    "income_sales_capacity": 0.20,
}


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(minimum, min(maximum, value))


def calculate_dimension_scores(
    signals: list[dict],
) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)

    for signal in signals:
        dimension = signal.get("dimension")
        score = signal.get("signal_score")

        if dimension not in DIMENSION_WEIGHTS:
            continue

        if score is None:
            continue

        try:
            score = float(score)
        except (TypeError, ValueError):
            continue

        grouped[dimension].append(
            clamp(score)
        )

    dimension_scores: dict[str, float] = {}

    for dimension, values in grouped.items():
        if not values:
            continue

        # Each signal represents observed financial behavior.
        # Multiple signals within one dimension are averaged.
        dimension_scores[dimension] = round(
            sum(values) / len(values),
            2,
        )

    return dimension_scores


def calculate_trust_score(
    dimension_scores: dict[str, float],
) -> float:
    weighted_total = 0.0
    available_weight = 0.0

    for dimension, score in dimension_scores.items():
        weight = DIMENSION_WEIGHTS.get(dimension)

        if weight is None:
            continue

        weighted_total += (
            score * weight
        )

        available_weight += weight

    if available_weight == 0:
        return 0.0

    # Missing dimensions are not interpreted as poor behavior.
    # Available dimensions are normalized against their available weight.
    trust_score = (
        weighted_total / available_weight
    )

    return round(
        clamp(trust_score),
        2,
    )


def calculate_dimension_contributions(
    dimension_scores: dict[str, float],
) -> dict[str, float]:
    contributions: dict[str, float] = {}

    available_weight = sum(
        DIMENSION_WEIGHTS.get(
            dimension,
            0.0,
        )
        for dimension in dimension_scores
    )

    if available_weight == 0:
        return contributions

    for dimension, score in dimension_scores.items():
        original_weight = DIMENSION_WEIGHTS.get(
            dimension,
            0.0,
        )

        normalized_weight = (
            original_weight / available_weight
        )

        contributions[dimension] = round(
            score * normalized_weight,
            2,
        )

    return contributions


def calculate_assessment(
    signals: list[dict],
) -> dict:
    dimension_scores = calculate_dimension_scores(
        signals
    )

    trust_score = calculate_trust_score(
        dimension_scores
    )

    contributions = calculate_dimension_contributions(
        dimension_scores
    )

    return {
        "trust_score": trust_score,
        "dimension_scores": dimension_scores,
        "dimension_contributions": contributions,
        "available_dimensions": list(
            dimension_scores.keys()
        ),
        "dimensions_with_evidence": len(
            dimension_scores
        ),
        "total_dimensions": len(
            DIMENSION_WEIGHTS
        ),
    }