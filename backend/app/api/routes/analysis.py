from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from backend.app.api.deps import get_authenticated_user
from backend.app.core.config import get_settings
from backend.app.schemas.analysis import EvidenceAnalysisResult
from backend.app.services.gemini import analyze_document
from backend.app.services.supabase import get_supabase_client
from backend.app.services.validation import validate_analysis


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
        .select("*")
        .eq("auth_user_id", str(user.id))
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
        file_bytes = (
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
        raw_analysis = analyze_document(
            file_bytes=file_bytes,
            mime_type=evidence["mime_type"],
        )

        analysis = EvidenceAnalysisResult.model_validate(
            raw_analysis
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Gemini returned data that failed validation.",
                "errors": exc.errors(),
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Document analysis failed: {exc}",
        ) from exc

    validation = validate_analysis(
        profile_name=profile["full_name"],
        category=evidence["category"],
        analysis=analysis,
    )

    evidence_status = "documented"

    if validation["authenticity_status"] in {
        "potential_manipulation",
        "inconclusive",
    }:
        evidence_status = "under_review"

    if validation["contradiction_detected"]:
        evidence_status = "under_review"

    now = datetime.now(timezone.utc).isoformat()

    try:
        supabase.table("extracted_facts").upsert(
            {
                "evidence_id": evidence_id,
                "document_type": analysis.document_type,
                "document_title": analysis.document_title,
                "extracted_data": analysis.facts.model_dump(),
                "extraction_confidence": analysis.authenticity.confidence,
                "ai_model": settings.ai_model,
                "updated_at": now,
            },
            on_conflict="evidence_id",
        ).execute()

        supabase.table("validation_results").upsert(
            {
                "evidence_id": evidence_id,
                "document_quality": None,
                "name_consistency": validation[
                    "name_consistency"
                ],
                "date_consistency": validation[
                    "date_consistency"
                ],
                "amount_consistency": validation[
                    "amount_consistency"
                ],
                "period_consistency": validation[
                    "period_consistency"
                ],
                "missing_fields": validation[
                    "missing_fields"
                ],
                "duplicate_detected": validation[
                    "duplicate_detected"
                ],
                "contradiction_detected": validation[
                    "contradiction_detected"
                ],
                "corroboration_count": validation[
                    "corroboration_count"
                ],
                "validation_notes": validation[
                    "validation_notes"
                ],
                "authenticity_status": validation[
                    "authenticity_status"
                ],
                "manipulation_indicators": validation[
                    "manipulation_indicators"
                ],
                "authenticity_confidence": validation[
                    "authenticity_confidence"
                ],
                "updated_at": now,
            },
            on_conflict="evidence_id",
        ).execute()

        supabase.table("evidence").update(
            {
                "status": evidence_status,
                "analyzed_at": now,
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
        "document_type": analysis.document_type,
        "document_title": analysis.document_title,
        "facts": analysis.facts.model_dump(),
        "authenticity": analysis.authenticity.model_dump(),
        "validation": validation,
        "status": evidence_status,
    }