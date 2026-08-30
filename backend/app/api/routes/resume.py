from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
from backend.app.services.resume import (
    build_financial_resume,
)
from backend.app.services.supabase import (
    get_supabase_client,
)


router = APIRouter(
    prefix="/resume",
    tags=["Financial Resume"],
)


@router.post("/generate")
def generate_resume(
    user=Depends(get_authenticated_user),
):
    supabase = get_supabase_client()

    # ---------------------------------------------------------
    # 1. Find profile
    # ---------------------------------------------------------

    profile_result = (
        supabase
        .table("profiles")
        .select("*")
        .eq(
            "auth_user_id",
            str(user.id),
        )
        .limit(1)
        .execute()
    )

    if not profile_result.data:
        raise HTTPException(
            status_code=404,
            detail="Financial profile not found.",
        )

    profile = profile_result.data[0]
    profile_id = profile["id"]

    # ---------------------------------------------------------
    # 2. Fetch evidence
    # ---------------------------------------------------------

    evidence_result = (
        supabase
        .table("evidence")
        .select("*")
        .eq(
            "profile_id",
            profile_id,
        )
        .order(
            "uploaded_at",
            desc=True,
        )
        .execute()
    )

    evidence = evidence_result.data or []

    # ---------------------------------------------------------
    # 3. Fetch financial signals
    # ---------------------------------------------------------

    signals_result = (
        supabase
        .table("financial_signals")
        .select("*")
        .eq(
            "profile_id",
            profile_id,
        )
        .execute()
    )

    signals = signals_result.data or []

    # ---------------------------------------------------------
    # 4. Fetch assessment
    # ---------------------------------------------------------

    assessment_result = (
        supabase
        .table("assessments")
        .select("*")
        .eq(
            "profile_id",
            profile_id,
        )
        .limit(1)
        .execute()
    )

    if not assessment_result.data:
        raise HTTPException(
            status_code=404,
            detail=(
                "Trust assessment not found. "
                "Calculate Trust before generating the Financial Resume."
            ),
        )

    stored_assessment = assessment_result.data[0]

    # ---------------------------------------------------------
    # 5. Fetch recommendations
    # ---------------------------------------------------------

    recommendations_result = (
        supabase
        .table("recommendations")
        .select("*")
        .eq(
            "profile_id",
            profile_id,
        )
        .order(
            "priority",
        )
        .execute()
    )

    recommendations = (
        recommendations_result.data or []
    )

    # ---------------------------------------------------------
    # 6. Build normalized assessment object
    # ---------------------------------------------------------

    assessment = {
        "trust_score": stored_assessment[
            "trust_score"
        ],
        "confidence_score": stored_assessment[
            "confidence_score"
        ],
        "dimension_scores": (
            stored_assessment.get(
                "dimension_scores"
            )
            or {}
        ),
        "positive_indicators": (
            stored_assessment.get(
                "positive_indicators"
            )
            or []
        ),
        "uncertainties": (
            stored_assessment.get(
                "uncertainties"
            )
            or []
        ),
        "explanation": stored_assessment.get(
            "explanation"
        ),
    }

    # ---------------------------------------------------------
    # 7. Build Financial Resume
    # ---------------------------------------------------------

    resume_data = build_financial_resume(
        profile=profile,
        evidence=evidence,
        assessment=assessment,
        signals=signals,
        recommendations=recommendations,
    )

    # ---------------------------------------------------------
    # 8. Determine next version
    # ---------------------------------------------------------

    existing_result = (
        supabase
        .table("financial_resumes")
        .select("version")
        .eq(
            "profile_id",
            profile_id,
        )
        .limit(1)
        .execute()
    )

    if existing_result.data:
        current_version = int(
            existing_result.data[0].get(
                "version",
                1,
            )
        )

        version = current_version + 1
    else:
        version = 1

    # ---------------------------------------------------------
    # 9. Persist resume
    # ---------------------------------------------------------

    result = (
        supabase
        .table("financial_resumes")
        .upsert(
            {
                "profile_id": profile_id,
                "resume_data": resume_data,
                "version": version,
            },
            on_conflict="profile_id",
        )
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Financial Resume could not be created.",
        )

    return {
        "id": result.data[0]["id"],
        "profile_id": profile_id,
        "version": version,
        "resume": resume_data,
    }


@router.get("")
def get_resume(
    user=Depends(get_authenticated_user),
):
    supabase = get_supabase_client()

    # ---------------------------------------------------------
    # 1. Find profile
    # ---------------------------------------------------------

    profile_result = (
        supabase
        .table("profiles")
        .select("id")
        .eq(
            "auth_user_id",
            str(user.id),
        )
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
    # 2. Fetch latest resume
    # ---------------------------------------------------------

    result = (
        supabase
        .table("financial_resumes")
        .select("*")
        .eq(
            "profile_id",
            profile_id,
        )
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Financial Resume not found.",
        )

    resume = result.data[0]

    return {
        "id": resume["id"],
        "profile_id": resume["profile_id"],
        "version": resume["version"],
        "resume": resume["resume_data"],
        "created_at": resume["created_at"],
        "updated_at": resume["updated_at"],
    }