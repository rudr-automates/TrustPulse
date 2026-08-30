from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
from backend.app.services.supabase import get_supabase_client
from backend.app.services.triangulation import (
    build_triangulation,
    count_corroboration,
)


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence Triangulation"],
)


@router.post("/triangulate")
def triangulate_evidence(
    user=Depends(get_authenticated_user),
):
    supabase = get_supabase_client()

    # ---------------------------------------------------------
    # 1. Find the authenticated user's profile
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
    # 2. Get all evidence belonging to this profile
    # ---------------------------------------------------------

    evidence_result = (
        supabase
        .table("evidence")
        .select("id, category, status")
        .eq("profile_id", profile_id)
        .execute()
    )

    evidence = evidence_result.data or []

    # Need at least two evidence items to compare anything
    if len(evidence) < 2:
        return {
            "relationships": [],
            "corroboration": {},
            "message": (
                "At least two evidence items are required "
                "for triangulation."
            ),
        }

    # ---------------------------------------------------------
    # 3. Get IDs for the evidence items
    # ---------------------------------------------------------

    evidence_ids = [
        item["id"]
        for item in evidence
    ]

    # ---------------------------------------------------------
    # 4. Get extracted facts for those evidence items
    # ---------------------------------------------------------

    facts_result = (
        supabase
        .table("extracted_facts")
        .select("*")
        .in_("evidence_id", evidence_ids)
        .execute()
    )

    facts_by_id = {
        item["evidence_id"]: item
        for item in (facts_result.data or [])
    }

    # ---------------------------------------------------------
    # 5. Combine the REAL evidence ID with its extracted facts
    #
    # Important:
    # extracted_facts.id is NOT the same as evidence.id.
    # We must preserve evidence_id for foreign-key writes.
    # ---------------------------------------------------------

    comparable_evidence = []

    for item in evidence:
        facts = facts_by_id.get(item["id"])

        if facts:
            comparable_evidence.append(
                {
                    "evidence_id": item["id"],
                    "extracted_data": facts.get(
                        "extracted_data",
                        {},
                    ),
                }
            )

    # If fewer than two documents have been analyzed,
    # triangulation cannot happen yet.
    if len(comparable_evidence) < 2:
        return {
            "relationships": [],
            "corroboration": {},
            "message": (
                "At least two analyzed evidence items "
                "are required for triangulation."
            ),
        }

    # ---------------------------------------------------------
    # 6. Build relationships
    # ---------------------------------------------------------

    relationships = build_triangulation(
        comparable_evidence
    )

    # ---------------------------------------------------------
    # 7. Count corroboration per evidence item
    # ---------------------------------------------------------

    corroboration_counts = count_corroboration(
        relationships
    )

    # ---------------------------------------------------------
    # 8. Persist evidence relationships
    # ---------------------------------------------------------

    for relationship in relationships:
        supabase.table("evidence_relations").upsert(
            {
                "source_evidence_id": relationship[
                    "source_evidence_id"
                ],
                "target_evidence_id": relationship[
                    "target_evidence_id"
                ],
                "relation_type": relationship[
                    "relation_type"
                ],
                "explanation": relationship[
                    "explanation"
                ],
            },
            on_conflict=(
                "source_evidence_id,"
                "target_evidence_id,"
                "relation_type"
            ),
        ).execute()

    # ---------------------------------------------------------
    # 9. Update corroboration counts
    # ---------------------------------------------------------

    for evidence_id, count in corroboration_counts.items():
        supabase.table("validation_results").update(
            {
                "corroboration_count": count,
            }
        ).eq(
            "evidence_id",
            evidence_id,
        ).execute()

    # ---------------------------------------------------------
    # 10. Return the triangulation result
    # ---------------------------------------------------------

    return {
        "relationships": relationships,
        "corroboration": corroboration_counts,
    }