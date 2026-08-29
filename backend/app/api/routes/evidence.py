from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.app.api.deps import get_authenticated_user
from backend.app.core.config import get_settings
from backend.app.schemas.evidence import EvidenceCategory, EvidenceResponse
from backend.app.services.supabase import get_supabase_client


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"],
)


ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_FILE_SIZE = 6 * 1024 * 1024


def get_user_profile_id(user_id: str) -> str:
    supabase = get_supabase_client()

    result = (
        supabase
        .table("profiles")
        .select("id")
        .eq("auth_user_id", user_id)
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Financial profile not found.",
        )

    return result.data[0]["id"]


@router.post("", response_model=EvidenceResponse)
async def upload_evidence(
    category: EvidenceCategory = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_authenticated_user),
):
    settings = get_settings()
    supabase = get_supabase_client()

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use PDF, JPG, JPEG, PNG, or DOCX.",
        )

    profile_id = get_user_profile_id(str(user.id))

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum size is 6 MB.",
        )

    extension = Path(file.filename).suffix.lower()

    if not extension:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file must have a valid extension.",
        )

    evidence_id = str(uuid4())
    storage_path = f"{user.id}/{evidence_id}{extension}"

    try:
        supabase.storage.from_(settings.storage_bucket).upload(
            path=storage_path,
            file=file_bytes,
            file_options={
                "content-type": file.content_type,
                "upsert": "false",
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Evidence file could not be uploaded.",
        ) from exc

    payload = {
        "id": evidence_id,
        "profile_id": profile_id,
        "category": category,
        "original_filename": file.filename,
        "mime_type": file.content_type,
        "storage_path": storage_path,
        "status": "uploaded",
    }

    try:
        result = (
            supabase
            .table("evidence")
            .insert(payload)
            .execute()
        )
    except Exception as exc:
        try:
            supabase.storage.from_(settings.storage_bucket).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Evidence metadata could not be created.",
        ) from exc

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Evidence record could not be created.",
        )

    return result.data[0]


@router.get("", response_model=list[EvidenceResponse])
def list_evidence(
    user=Depends(get_authenticated_user),
):
    supabase = get_supabase_client()

    profile_id = get_user_profile_id(str(user.id))

    result = (
        supabase
        .table("evidence")
        .select("*")
        .eq("profile_id", profile_id)
        .order("uploaded_at", desc=True)
        .execute()
    )

    return result.data or []


@router.delete("/{evidence_id}")
def delete_evidence(
    evidence_id: str,
    user=Depends(get_authenticated_user),
):
    settings = get_settings()
    supabase = get_supabase_client()

    profile_id = get_user_profile_id(str(user.id))

    result = (
        supabase
        .table("evidence")
        .select("*")
        .eq("id", evidence_id)
        .eq("profile_id", profile_id)
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    evidence = result.data[0]
    storage_path = evidence["storage_path"]

    try:
        supabase.storage.from_(settings.storage_bucket).remove(
            [storage_path]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Evidence file could not be deleted from storage.",
        ) from exc

    supabase.table("evidence").delete().eq(
        "id",
        evidence_id,
    ).eq(
        "profile_id",
        profile_id,
    ).execute()

    return {
        "status": "deleted",
        "evidence_id": evidence_id,
    }