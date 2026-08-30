from typing import Any


DIMENSION_LABELS = {
    "repayment_reliability": "Repayment Reliability",
    "payment_discipline": "Payment Discipline",
    "business_continuity": "Business Continuity",
    "income_sales_capacity": "Income & Sales Capacity",
}


def build_recommendations(
    *,
    dimension_scores: dict[str, float],
    confidence_score: float,
    validation_results: list[dict],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # 1. Identify weak / missing dimensions
    # ---------------------------------------------------------

    all_dimensions = set(DIMENSION_LABELS.keys())

    for dimension in all_dimensions:
        label = DIMENSION_LABELS[dimension]

        if dimension not in dimension_scores:
            recommendations.append(
                {
                    "recommendation_type": "missing_evidence",
                    "title": f"Add {label} evidence",
                    "description": (
                        f"Add recent evidence that helps establish "
                        f"{label.lower()}."
                    ),
                    "priority": "high",
                    "source_dimension": dimension,
                }
            )
            continue

        score = float(
            dimension_scores[dimension]
        )

        if score < 60:
            recommendations.append(
                {
                    "recommendation_type": "strengthen_dimension",
                    "title": f"Strengthen {label}",
                    "description": (
                        f"Add more recent, reliable evidence related to "
                        f"{label.lower()} and maintain consistent financial activity."
                    ),
                    "priority": "medium",
                    "source_dimension": dimension,
                }
            )

    # ---------------------------------------------------------
    # 2. Handle evidence quality / authenticity uncertainty
    # ---------------------------------------------------------

    under_review_count = 0
    inconclusive_count = 0
    manipulation_count = 0

    for validation in validation_results:
        authenticity_status = validation.get(
            "authenticity_status"
        )

        if authenticity_status in {
            "inconclusive",
            "potential_manipulation",
        }:
            under_review_count += 1

        if authenticity_status == "inconclusive":
            inconclusive_count += 1

        if authenticity_status == "potential_manipulation":
            manipulation_count += 1

    if under_review_count > 0:
        recommendations.append(
            {
                "recommendation_type": "resolve_evidence_review",
                "title": "Resolve evidence under review",
                "description": (
                    "Review documents currently marked under review and "
                    "replace unclear or suspicious records with clearer supporting evidence."
                ),
                "priority": "high",
                "source_dimension": None,
            }
        )

    if inconclusive_count > 0:
        recommendations.append(
            {
                "recommendation_type": "improve_document_quality",
                "title": "Improve document quality",
                "description": (
                    "Provide clearer or higher-quality copies of documents "
                    "whose authenticity could not be assessed confidently."
                ),
                "priority": "medium",
                "source_dimension": None,
            }
        )

    if manipulation_count > 0:
        recommendations.append(
            {
                "recommendation_type": "replace_suspicious_document",
                "title": "Replace suspicious evidence",
                "description": (
                    "Replace documents showing potential manipulation indicators "
                    "with original records obtained directly from the relevant source."
                ),
                "priority": "high",
                "source_dimension": None,
            }
        )

    # ---------------------------------------------------------
    # 3. Confidence-based recommendation
    # ---------------------------------------------------------

    if confidence_score < 60:
        recommendations.append(
            {
                "recommendation_type": "increase_confidence",
                "title": "Increase evidence confidence",
                "description": (
                    "Add more recent and independently corroborating records "
                    "to strengthen confidence in your financial profile."
                ),
                "priority": "medium",
                "source_dimension": None,
            }
        )

    # ---------------------------------------------------------
    # 4. If the profile is already reasonably supported
    # ---------------------------------------------------------

    if (
        confidence_score >= 75
        and not recommendations
    ):
        recommendations.append(
            {
                "recommendation_type": "maintain_profile",
                "title": "Keep your financial record current",
                "description": (
                    "Continue adding recent records so your Financial Resume "
                    "remains current and well-supported."
                ),
                "priority": "low",
                "source_dimension": None,
            }
        )

    # ---------------------------------------------------------
    # 5. Remove exact duplicate recommendations
    # ---------------------------------------------------------

    unique: list[dict[str, Any]] = []
    seen: set[str] = set()

    for recommendation in recommendations:
        key = recommendation["title"]

        if key in seen:
            continue

        seen.add(key)
        unique.append(recommendation)

    # ---------------------------------------------------------
    # 6. Limit MVP output
    # ---------------------------------------------------------

    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    unique.sort(
        key=lambda item: priority_order.get(
            item["priority"],
            99,
        )
    )

    return unique[:6]