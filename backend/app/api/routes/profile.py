from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
from backend.app.schemas.profile import ProfileCreate, ProfileResponse
from backend.app.services.supabase import get_supabase_client


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.post("", response_model=ProfileResponse)
def create_profile(
    profile: ProfileCreate,
    user=Depends(get_authenticated_user),
):
    supabase = get_supabase_client()

    existing = (
        supabase.table("profiles")
        .select("*")
        .eq("auth_user_id", str(user.id))
        .limit(1)
        .execute()
    )

    if existing.data:
        raise HTTPException(
            status_code=409,
            detail="A profile already exists for this user.",
        )

    payload = {
        "auth_user_id": str(user.id),
        "full_name": profile.full_name,
        "occupation": profile.occupation,
        "years_in_business": profile.years_in_business,
        "location": profile.location,
        "language": profile.language,
        "consent_accepted": profile.consent_accepted,
    }

    result = (
        supabase
        .table("profiles")
        .insert(payload)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Profile could not be created.",
        )

    return result.data[0]


@router.get("", response_model=ProfileResponse)
def get_profile(
    user=Depends(get_authenticated_user),
):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("profiles")
        .select("*")
        .eq("auth_user_id", str(user.id))
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )

    return result.data[0]