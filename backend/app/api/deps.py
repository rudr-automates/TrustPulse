from fastapi import Header, HTTPException

from backend.app.services.supabase import get_supabase_client


def get_authenticated_user(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required.",
        )

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must use Bearer token.",
        )

    token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Bearer token is missing.",
        )

    supabase = get_supabase_client()

    try:
        response = supabase.auth.get_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
        ) from exc

    if not response.user:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user could not be resolved.",
        )

    return response.user