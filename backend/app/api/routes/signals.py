from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import get_authenticated_user
from backend.app.services.signals import build_signal
from backend.app.services.supabase import get_supabase_client


router = APIRouter(
    prefix="/evidence",
    tags=["Financial Signals"],
)


@router.post("/generate-signals")
def generate_signals(
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
    # 2. Fetch evidence
    # ---------------------------------------------------------

    evidence_result = (
        supabase
        .table("evidence")
        .select("*")
        .eq("profile_id", profile_id)
        .execute()
    )

    evidence = evidence_result.data or []

    if not evidence:
        return {
            "signals": [],
            "message": "No evidence is available.",
        }

    evidence_ids = [
        item["id"]
        for item in evidence
    ]

    # ---------------------------------------------------------
    # 3. Fetch extracted facts
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
    # 4. Fetch validation results
    # ---------------------------------------------------------

    validation_result = (
        supabase
        .table("validation_results")
        .select("*")
        .in_("evidence_id", evidence_ids)
        .execute()
    )

    validation_by_id = {
        item["evidence_id"]: item
        for item in (validation_result.data or [])
    }

    # ---------------------------------------------------------
    # 5. Fetch corroboration counts
    # ---------------------------------------------------------

    relations_result = (
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

    corroboration_counts = {
        evidence_id: 0
        for evidence_id in evidence_ids
    }

    for relation in relations_result.data or []:
        if relation["relation_type"] != "corroborates":
            continue

        source_id = relation["source_evidence_id"]
        target_id = relation["target_evidence_id"]

        if source_id in corroboration_counts:
            corroboration_counts[source_id] += 1

        if target_id in corroboration_counts:
            corroboration_counts[target_id] += 1

    # ---------------------------------------------------------
    # 6. Generate signals
    # ---------------------------------------------------------

    signals = []

    for evidence_item in evidence:
        evidence_id = evidence_item["id"]

        facts_record = facts_by_id.get(evidence_id)

        if not facts_record:
            continue

        extracted_facts = (
            facts_record.get("extracted_data")
            or {}
        )

        validation = (
            validation_by_id.get(evidence_id)
            or {}
        )

        signal = build_signal(
            evidence=evidence_item,
            extracted_facts=extracted_facts,
            validation=validation,
            corroboration_count=corroboration_counts.get(
                evidence_id,
                0,
            ),
        )

        if signal is not None:
            signal["profile_id"] = profile_id
            signals.append(signal)

    # ---------------------------------------------------------
    # 7. Replace previous generated signals
    # ---------------------------------------------------------

    supabase.table("financial_signals").delete().eq(
        "profile_id",
        profile_id,
    ).execute()

    # ---------------------------------------------------------
    # 8. Save new signals
    # ---------------------------------------------------------

    if signals:
        supabase.table("financial_signals").insert(
            signals
        ).execute()

    return {
        "signals": signals,
        "signal_count": len(signals),
    }