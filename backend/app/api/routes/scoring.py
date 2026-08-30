from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
from backend.app.services.confidence import calculate_confidence
from backend.app.services.explainability import (
    build_explanation_package,
)
from backend.app.services.scoring import calculate_assessment
from backend.app.services.supabase import get_supabase_client


router = APIRouter(
    prefix="/trust",
    tags=["Trust Scoring"],
)


@router.post("/calculate")
def calculate_trust(
    user=Depends(get_authenticated_user),
):
    supabase = get_supabase_client()

    # ---------------------------------------------------------
    # 1. Find borrower profile
    # ---------------------------------------------------------

    profile_result = (
        supabase
        .table("profiles")
        .select("id")
        .eq("auth_user_id", str(user.id))
        .limit(1)
        .execute()
    )

    if not profile_result.data:
        raise HTTPException(
            status_code=404,
            detail="Financial profile not found.",
        )

    profile_id = profile_result.data[0]["id"]

    # ---------------------------------------------------------
    # 2. Fetch financial signals
    # ---------------------------------------------------------

    signals_result = (
        supabase
        .table("financial_signals")
        .select("*")
        .eq("profile_id", profile_id)
        .execute()
    )

    signals = signals_result.data or []

    if not signals:
        return {
            "trust_score": 0,
            "confidence_score": 0,
            "dimension_scores": {},
            "dimension_contributions": {},
            "available_dimensions": [],
            "dimensions_with_evidence": 0,
            "total_dimensions": 4,
            "confidence_components": {},
            "positive_indicators": [],
            "uncertainties": [
                "No financial evidence has been analyzed yet."
            ],
            "explanation": (
                "TrustPulse cannot produce a meaningful assessment "
                "until financial evidence is available."
            ),
            "message": "No financial signals are available yet.",
        }

    # ---------------------------------------------------------
    # 3. Calculate Trust
    # ---------------------------------------------------------

    assessment = calculate_assessment(
        signals
    )

    # ---------------------------------------------------------
    # 4. Determine evidence IDs represented by signals
    # ---------------------------------------------------------

    evidence_ids: list[str] = []

    for signal in signals:
        for evidence_id in (
            signal.get("evidence_ids") or []
        ):
            if evidence_id not in evidence_ids:
                evidence_ids.append(
                    evidence_id
                )

    # ---------------------------------------------------------
    # 5. Fetch validation results
    # ---------------------------------------------------------

    validation_results: list[dict] = []

    if evidence_ids:
        validation_query = (
            supabase
            .table("validation_results")
            .select("*")
            .in_("evidence_id", evidence_ids)
            .execute()
        )

        validation_results = (
            validation_query.data or []
        )

    # ---------------------------------------------------------
    # 6. Calculate corroboration counts
    # ---------------------------------------------------------

    corroboration_by_evidence = {
        evidence_id: 0
        for evidence_id in evidence_ids
    }

    if evidence_ids:
        relations_query = (
            supabase
            .table("evidence_relations")
            .select(
                "source_evidence_id, "
                "target_evidence_id, "
                "relation_type"
            )
            .or_(
                "source_evidence_id.in.("
                + ",".join(evidence_ids)
                + "),"
                "target_evidence_id.in.("
                + ",".join(evidence_ids)
                + ")"
            )
            .execute()
        )

        for relation in (
            relations_query.data or []
        ):
            if relation["relation_type"] != "corroborates":
                continue

            source_id = relation[
                "source_evidence_id"
            ]

            target_id = relation[
                "target_evidence_id"
            ]

            if source_id in corroboration_by_evidence:
                corroboration_by_evidence[
                    source_id
                ] += 1

            if target_id in corroboration_by_evidence:
                corroboration_by_evidence[
                    target_id
                ] += 1

    # ---------------------------------------------------------
    # 7. Calculate Confidence
    # ---------------------------------------------------------

    confidence = calculate_confidence(
        signals=signals,
        validation_results=validation_results,
    )

    confidence_score = confidence[
        "confidence_score"
    ]

    # ---------------------------------------------------------
    # 8. Build explainability package
    # ---------------------------------------------------------

    explanation = build_explanation_package(
        trust_score=assessment["trust_score"],
        confidence_score=confidence_score,
        dimension_scores=assessment[
            "dimension_scores"
        ],
        signals=signals,
        validation_results=validation_results,
        corroboration_by_evidence=(
            corroboration_by_evidence
        ),
    )

    # ---------------------------------------------------------
    # 9. Persist complete assessment
    # ---------------------------------------------------------

    result = (
        supabase
        .table("assessments")
        .upsert(
            {
                "profile_id": profile_id,
                "trust_score": assessment[
                    "trust_score"
                ],
                "confidence_score": confidence_score,
                "dimension_scores": assessment[
                    "dimension_scores"
                ],
                "positive_indicators": explanation[
                    "positive_indicators"
                ],
                "uncertainties": explanation[
                    "uncertainties"
                ],
                "explanation": explanation[
                    "explanation"
                ],
            },
            on_conflict="profile_id",
        )
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Trust assessment could not be saved.",
        )

    # ---------------------------------------------------------
    # 10. Return complete borrower-facing assessment
    # ---------------------------------------------------------

    return {
        **assessment,
        "confidence_score": confidence_score,
        "confidence_components": confidence[
            "components"
        ],
        "positive_indicators": explanation[
            "positive_indicators"
        ],
        "uncertainties": explanation[
            "uncertainties"
        ],
        "explanation": explanation[
            "explanation"
        ],
    }