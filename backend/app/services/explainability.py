from typing import Any


DIMENSION_LABELS = {
    "repayment_reliability": "Repayment Reliability",
    "payment_discipline": "Payment Discipline",
    "business_continuity": "Business Continuity",
    "income_sales_capacity": "Income & Sales Capacity",
}


def dimension_label(dimension: str) -> str:
    return DIMENSION_LABELS.get(
        dimension,
        dimension.replace("_", " ").title(),
    )


def unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        cleaned = value.strip()

        if not cleaned:
            continue

        if cleaned in seen:
            continue

        seen.add(cleaned)
        result.append(cleaned)

    return result


def build_positive_indicators(
    signals: list[dict],
    corroboration_by_evidence: dict[str, int],
) -> list[str]:
    indicators: list[str] = []

    for signal in signals:
        dimension = signal.get("dimension")
        score = signal.get("signal_score")

        if dimension not in DIMENSION_LABELS:
            continue

        try:
            score_value = float(score)
        except (TypeError, ValueError):
            continue

        label = dimension_label(dimension)

        if score_value >= 75:
            indicators.append(
                f"Strong observed {label.lower()} signal."
            )

        elif score_value >= 60:
            indicators.append(
                f"Positive observed {label.lower()} signal."
            )

        for evidence_id in signal.get(
            "evidence_ids",
            [],
        ):
            corroboration_count = corroboration_by_evidence.get(
                evidence_id,
                0,
            )

            if corroboration_count > 0:
                indicators.append(
                    f"{corroboration_count} additional record(s) "
                    f"provide corroborating support for the {label.lower()} evidence."
                )

    return unique_strings(indicators)


def build_uncertainties(
    signals: list[dict],
    validation_results: list[dict],
    available_dimensions: list[str],
) -> list[str]:
    uncertainties: list[str] = []

    # ---------------------------------------------------------
    # Missing dimensions
    # ---------------------------------------------------------

    all_dimensions = set(DIMENSION_LABELS.keys())
    missing_dimensions = [
        dimension
        for dimension in all_dimensions
        if dimension not in available_dimensions
    ]

    for dimension in sorted(
        missing_dimensions
    ):
        uncertainties.append(
            f"Limited evidence is available for "
            f"{dimension_label(dimension).lower()}."
        )

    # ---------------------------------------------------------
    # Evidence-level issues
    # ---------------------------------------------------------

    for validation in validation_results:
        authenticity_status = validation.get(
            "authenticity_status"
        )

        if authenticity_status == "potential_manipulation":
            uncertainties.append(
                "Potential manipulation indicators were identified "
                "in one or more submitted documents."
            )

        elif authenticity_status == "inconclusive":
            uncertainties.append(
                "The authenticity of one or more submitted documents "
                "could not be determined confidently."
            )

        if validation.get(
            "contradiction_detected"
        ):
            uncertainties.append(
                "One or more consistency checks identified conflicting "
                "or anomalous information."
            )

        missing_fields = validation.get(
            "missing_fields"
        ) or []

        if missing_fields:
            uncertainties.append(
                "Some expected information was missing from one or more "
                "submitted documents."
            )

    return unique_strings(uncertainties)


def build_explanation(
    *,
    trust_score: float,
    confidence_score: float,
    dimension_scores: dict[str, float],
    positive_indicators: list[str],
    uncertainties: list[str],
) -> str:
    strongest_dimension = None
    strongest_score = -1.0

    for dimension, score in dimension_scores.items():
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            continue

        if numeric_score > strongest_score:
            strongest_score = numeric_score
            strongest_dimension = dimension

    explanation_parts: list[str] = []

    explanation_parts.append(
        f"TrustPulse currently assesses this financial profile "
        f"at {round(trust_score, 2)}/100 Trust with "
        f"{round(confidence_score, 2)}/100 Confidence."
    )

    if strongest_dimension is not None:
        explanation_parts.append(
            f"The strongest observed dimension is "
            f"{dimension_label(strongest_dimension)}."
        )

    if positive_indicators:
        explanation_parts.append(
            "Positive indicators are supported by the submitted evidence."
        )

    if uncertainties:
        explanation_parts.append(
            "Confidence remains limited by evidence coverage, "
            "quality, consistency, or authenticity uncertainty."
        )
    else:
        explanation_parts.append(
            "No major uncertainty was identified in the current assessment."
        )

    return " ".join(explanation_parts)


def build_explanation_package(
    *,
    trust_score: float,
    confidence_score: float,
    dimension_scores: dict[str, float],
    signals: list[dict],
    validation_results: list[dict],
    corroboration_by_evidence: dict[str, int],
) -> dict[str, Any]:
    available_dimensions = list(
        dimension_scores.keys()
    )

    positive_indicators = build_positive_indicators(
        signals=signals,
        corroboration_by_evidence=corroboration_by_evidence,
    )

    uncertainties = build_uncertainties(
        signals=signals,
        validation_results=validation_results,
        available_dimensions=available_dimensions,
    )

    explanation = build_explanation(
        trust_score=trust_score,
        confidence_score=confidence_score,
        dimension_scores=dimension_scores,
        positive_indicators=positive_indicators,
        uncertainties=uncertainties,
    )

    return {
        "positive_indicators": positive_indicators,
        "uncertainties": uncertainties,
        "explanation": explanation,
    }