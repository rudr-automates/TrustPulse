from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


AuthenticityStatus = Literal[
    "no_significant_indicators",
    "potential_manipulation",
    "inconclusive",
]


class AuthenticityAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AuthenticityStatus
    confidence: float = Field(ge=0, le=100)
    indicators: list[str] = Field(default_factory=list)


class ExtractedFacts(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    date: str | None = None
    amount: float | None = None
    currency: str | None = None
    reference_number: str | None = None

    repayment_details: dict[str, Any] | None = None
    payment_details: dict[str, Any] | None = None
    business_details: dict[str, Any] | None = None
    income_details: dict[str, Any] | None = None
    tax_details: dict[str, Any] | None = None


class EvidenceAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str | None = None
    document_title: str | None = None

    facts: ExtractedFacts = Field(
        default_factory=ExtractedFacts
    )

    authenticity: AuthenticityAssessment