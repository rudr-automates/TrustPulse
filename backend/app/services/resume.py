from typing import Any


DIMENSION_LABELS = {
    "repayment_reliability": "Repayment Reliability",
    "payment_discipline": "Payment Discipline",
    "business_continuity": "Business Continuity",
    "income_sales_capacity": "Income & Sales Capacity",
}


def build_financial_resume(
    *,
    profile: dict,
    evidence: list[dict],
    assessment: dict,
    signals: list[dict],
    recommendations: list[dict],
) -> dict[str, Any]:
    dimension_scores = (
        assessment.get("dimension_scores")
        or {}
    )

    resume_dimensions = []

    for dimension, score in dimension_scores.items():
        resume_dimensions.append(
            {
                "dimension": dimension,
                "label": DIMENSION_LABELS.get(
                    dimension,
                    dimension.replace("_", " ").title(),
                ),
                "score": score,
            }
        )

    evidence_summary = []

    for item in evidence:
        evidence_summary.append(
            {
                "id": item["id"],
                "category": item["category"],
                "filename": item["original_filename"],
                "status": item["status"],
            }
        )

    signal_summary = []

    for signal in signals:
        signal_summary.append(
            {
                "dimension": signal["dimension"],
                "signal_type": signal["signal_type"],
                "signal_score": signal["signal_score"],
                "strength": signal["strength"],
                "evidence_ids": signal.get(
                    "evidence_ids",
                    [],
                ),
            }
        )

    recommendation_summary = []

    for recommendation in recommendations:
        recommendation_summary.append(
            {
                "type": recommendation[
                    "recommendation_type"
                ],
                "title": recommendation["title"],
                "description": recommendation[
                    "description"
                ],
                "priority": recommendation["priority"],
                "source_dimension": recommendation.get(
                    "source_dimension"
                ),
            }
        )

    return {
        "identity": {
            "full_name": profile["full_name"],
            "occupation": profile["occupation"],
            "years_in_business": profile[
                "years_in_business"
            ],
            "location": profile["location"],
            "language": profile["language"],
        },
        "assessment": {
            "trust_score": assessment[
                "trust_score"
            ],
            "confidence_score": assessment[
                "confidence_score"
            ],
            "dimension_scores": resume_dimensions,
        },
        "evidence": {
            "total_count": len(evidence),
            "items": evidence_summary,
        },
        "financial_signals": signal_summary,
        "positive_indicators": assessment.get(
            "positive_indicators",
            [],
        ),
        "uncertainties": assessment.get(
            "uncertainties",
            [],
        ),
        "explanation": assessment.get(
            "explanation"
        ),
        "recommendations": recommendation_summary,
    }