from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
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
            "dimension_scores": {},
            "dimension_contributions": {},
            "available_dimensions": [],
            "dimensions_with_evidence": 0,
            "total_dimensions": 4,
            "message": "No financial signals are available yet.",
        }

    # ---------------------------------------------------------
    # 3. Calculate deterministic assessment
    # ---------------------------------------------------------

    assessment = calculate_assessment(signals)

    # ---------------------------------------------------------
    # 4. Save assessment
    # ---------------------------------------------------------

    result = (
        supabase
        .table("assessments")
        .upsert(
            {
                "profile_id": profile_id,
                "trust_score": assessment["trust_score"],
                "confidence_score": 0,
                "dimension_scores": assessment[
                    "dimension_scores"
                ],
                "positive_indicators": [],
                "uncertainties": [],
                "explanation": None,
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

    return assessment