import re
from datetime import date, datetime

from backend.app.schemas.analysis import EvidenceAnalysisResult


def normalize_text(
    value: str | None,
) -> str:
    if not value:
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        value.lower(),
    ).strip()


def names_consistent(
    profile_name: str,
    extracted_name: str | None,
) -> bool | None:
    if not extracted_name:
        return None

    profile_tokens = set(
        normalize_text(profile_name).split()
    )

    extracted_tokens = set(
        normalize_text(extracted_name).split()
    )

    if not profile_tokens or not extracted_tokens:
        return None

    if normalize_text(profile_name) == normalize_text(
        extracted_name
    ):
        return True

    overlap = profile_tokens.intersection(
        extracted_tokens
    )

    return len(overlap) >= max(
        1,
        min(
            len(profile_tokens),
            len(extracted_tokens),
        ),
    )


def identity_status(
    name_consistency: bool | None,
) -> str:
    if name_consistency is True:
        return "matched"

    if name_consistency is False:
        return "mismatch"

    return "not_available"


def date_is_sane(
    extracted_date: str | None,
) -> bool | None:
    if not extracted_date:
        return None

    try:
        parsed = datetime.fromisoformat(
            extracted_date
        ).date()
    except ValueError:
        try:
            parsed = date.fromisoformat(
                extracted_date
            )
        except ValueError:
            return False

    return parsed <= date.today()


def amount_is_sane(
    amount: float | None,
) -> bool | None:
    if amount is None:
        return None

    return amount >= 0


def expected_missing_fields(
    category: str,
    analysis: EvidenceAnalysisResult,
) -> list[str]:
    facts = analysis.facts
    missing: list[str] = []

    if not analysis.document_type:
        missing.append("document_type")

    requirements: dict[str, list[str]] = {
        "repayment": [
            "date",
            "amount",
        ],
        "recurring_payment": [
            "date",
            "amount",
        ],
        "business": [
            "date",
        ],
        "income_sales": [
            "date",
            "amount",
        ],
        "tax": [
            "date",
            "amount",
        ],
        "asset": [
            "date",
        ],
    }

    for field in requirements.get(
        category,
        [],
    ):
        value = getattr(
            facts,
            field,
            None,
        )

        if value is None:
            missing.append(field)

    return missing


def normalize_authenticity(
    status: str,
    confidence: float,
    indicators: list[str],
) -> tuple[str, float, list[str]]:
    valid_statuses = {
        "no_significant_indicators",
        "potential_manipulation",
        "inconclusive",
    }

    if status not in valid_statuses:
        status = "inconclusive"

    confidence = max(
        0.0,
        min(
            100.0,
            float(confidence),
        ),
    )

    cleaned_indicators = [
        str(item).strip()
        for item in indicators
        if str(item).strip()
    ]

    if (
        status == "potential_manipulation"
        and not cleaned_indicators
    ):
        cleaned_indicators = [
            "Potential manipulation was flagged, but no specific indicator was returned."
        ]

    if (
        status == "no_significant_indicators"
        and cleaned_indicators
    ):
        status = "potential_manipulation"

    return (
        status,
        confidence,
        cleaned_indicators,
    )


def validate_analysis(
    *,
    profile_name: str,
    category: str,
    analysis: EvidenceAnalysisResult,
) -> dict:
    name_consistency = names_consistent(
        profile_name,
        analysis.facts.name,
    )

    identity = identity_status(
        name_consistency
    )

    date_consistency = date_is_sane(
        analysis.facts.date,
    )

    amount_consistency = amount_is_sane(
        analysis.facts.amount,
    )

    missing_fields = expected_missing_fields(
        category,
        analysis,
    )

    contradictions: list[str] = []

    if identity == "mismatch":
        contradictions.append(
            "The document name does not match the authenticated borrower profile."
        )

    if date_consistency is False:
        contradictions.append(
            "The extracted document date is invalid or appears to be in the future."
        )

    if amount_consistency is False:
        contradictions.append(
            "The extracted amount is invalid."
        )

    contradiction_detected = bool(
        contradictions
    )

    (
        authenticity_status,
        authenticity_confidence,
        manipulation_indicators,
    ) = normalize_authenticity(
        status=analysis.authenticity.status,
        confidence=analysis.authenticity.confidence,
        indicators=analysis.authenticity.indicators,
    )

    notes: list[str] = []

    if identity == "matched":
        notes.append(
            "The document name matches the authenticated borrower profile."
        )

    elif identity == "mismatch":
        notes.append(
            "The document name does not match the authenticated borrower profile."
        )

    else:
        notes.append(
            "A borrower name was not available for deterministic identity comparison."
        )

    if missing_fields:
        notes.append(
            "Some expected information was not available in the extracted document."
        )

    if contradiction_detected:
        notes.append(
            "One or more deterministic consistency checks identified an issue."
        )
    else:
        notes.append(
            "No deterministic financial/document consistency contradiction was identified."
        )

    if authenticity_status == "potential_manipulation":
        notes.append(
            "The authenticity assessment identified potential manipulation indicators."
        )

    elif authenticity_status == "inconclusive":
        notes.append(
            "The authenticity assessment was inconclusive."
        )

    return {
        "name_consistency": name_consistency,
        "identity_status": identity,
        "date_consistency": date_consistency,
        "amount_consistency": amount_consistency,
        "period_consistency": None,
        "missing_fields": missing_fields,
        "duplicate_detected": False,
        "contradiction_detected": contradiction_detected,
        "corroboration_count": 0,
        "validation_notes": " ".join(notes),
        "authenticity_status": authenticity_status,
        "manipulation_indicators": manipulation_indicators,
        "authenticity_confidence": authenticity_confidence,
    }