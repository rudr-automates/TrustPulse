from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
from backend.app.core.config import get_settings
from backend.app.services.gemini import analyze_document
from backend.app.services.supabase import get_supabase_client
from datetime import datetime, timezone


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence Analysis"],
)


@router.post("/{evidence_id}/analyze")
def analyze_evidence(
    evidence_id: str,
    user=Depends(get_authenticated_user),
):
    settings = get_settings()
    supabase = get_supabase_client()

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

    evidence_result = (
        supabase
        .table("evidence")
        .select("*")
        .eq("id", evidence_id)
        .eq("profile_id", profile_id)
        .limit(1)
        .execute()
    )

    if not evidence_result.data:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    evidence = evidence_result.data[0]

    try:
        file_response = (
            supabase
            .storage
            .from_(settings.storage_bucket)
            .download(evidence["storage_path"])
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Evidence file could not be retrieved.",
        ) from exc

    try:
        analysis = analyze_document(
            file_bytes=file_response,
            mime_type=evidence["mime_type"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Document analysis failed: {exc}",
        ) from exc

    authenticity = analysis.get("authenticity", {})

    try:
        supabase.table("extracted_facts").upsert(
            {
                "evidence_id": evidence_id,
                "document_type": analysis.get("document_type"),
                "document_title": analysis.get("document_title"),
                "extracted_data": analysis.get("facts", {}),
                "extraction_confidence": authenticity.get(
                    "confidence"
                ),
                "ai_model": settings.ai_model,
            },
            on_conflict="evidence_id",
        ).execute()

        supabase.table("validation_results").upsert(
            {
                "evidence_id": evidence_id,
                "authenticity_status": authenticity.get(
                    "status",
                    "inconclusive",
                ),
                "manipulation_indicators": authenticity.get(
                    "indicators",
                    [],
                ),
                "authenticity_confidence": authenticity.get(
                    "confidence"
                ),
            },
            on_conflict="evidence_id",
        ).execute()

        supabase.table("evidence").update(
            {
                "status": "documented",
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq(
            "id",
            evidence_id,
        ).eq(
            "profile_id",
            profile_id,
        ).execute()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Analysis results could not be saved.",
        ) from exc

    return {
        "evidence_id": evidence_id,
        "document_type": analysis.get("document_type"),
        "document_title": analysis.get("document_title"),
        "facts": analysis.get("facts", {}),
        "authenticity": authenticity,
        "status": "documented",
    }