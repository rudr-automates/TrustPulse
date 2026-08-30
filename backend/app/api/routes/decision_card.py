from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
from backend.app.services.decision_card import (
    build_decision_card,
)
from backend.app.services.supabase import (
    get_supabase_client,
)


router = APIRouter(
    prefix="/decision-card",
    tags=["Decision Card"],
)


@router.post("/generate")
def generate_decision_card(
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
    # 2. Get latest Financial Resume
    # ---------------------------------------------------------

    resume_result = (
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

    if not resume_result.data:
        raise HTTPException(
            status_code=404,
            detail=(
                "Financial Resume not found. "
                "Generate the Financial Resume first."
            ),
        )

    resume_record = resume_result.data[0]

    resume_data = resume_record["resume_data"]

    # ---------------------------------------------------------
    # 3. Build Decision Card
    # ---------------------------------------------------------

    card_data = build_decision_card(
        profile=profile,
        resume=resume_data,
    )

    # ---------------------------------------------------------
    # 4. Persist
    # ---------------------------------------------------------

    result = (
        supabase
        .table("decision_cards")
        .upsert(
            {
                "profile_id": profile_id,
                "resume_id": resume_record["id"],
                "card_data": card_data,
            },
            on_conflict="profile_id",
        )
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Decision Card could not be created.",
        )

    return {
        "id": result.data[0]["id"],
        "profile_id": profile_id,
        "resume_id": resume_record["id"],
        "card": card_data,
    }


@router.get("")
def get_decision_card(
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
    # 2. Fetch card
    # ---------------------------------------------------------

    result = (
        supabase
        .table("decision_cards")
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
            detail="Decision Card not found.",
        )

    record = result.data[0]

    return {
        "id": record["id"],
        "profile_id": record["profile_id"],
        "resume_id": record["resume_id"],
        "card": record["card_data"],
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
    }