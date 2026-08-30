from typing import Any


def build_decision_card(
    *,
    profile: dict,
    resume: dict,
) -> dict[str, Any]:
    assessment = resume.get("assessment", {})

    return {
        "borrower": {
            "full_name": profile["full_name"],
            "occupation": profile["occupation"],
            "location": profile["location"],
        },
        "trust": {
            "score": assessment.get("trust_score", 0),
            "confidence": assessment.get(
                "confidence_score",
                0,
            ),
            "dimensions": assessment.get(
                "dimension_scores",
                [],
            ),
        },
        "summary": {
            "evidence_count": (
                resume.get("evidence", {})
                .get("total_count", 0)
            ),
            "positive_indicators": resume.get(
                "positive_indicators",
                [],
            ),
            "uncertainties": resume.get(
                "uncertainties",
                [],
            ),
        },
        "recommendations": resume.get(
            "recommendations",
            [],
        ),
        "explanation": resume.get(
            "explanation"
        ),
        "disclaimer": (
            "TrustPulse provides an evidence-based financial "
            "assessment. Document authenticity assessment is "
            "AI-assisted and does not constitute forensic or "
            "legal authentication."
        ),
    }