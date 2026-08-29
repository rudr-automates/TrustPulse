from typing import Literal

from pydantic import BaseModel


EvidenceCategory = Literal[
    "repayment",
    "recurring_payment",
    "business",
    "income_sales",
    "tax",
    "asset",
    "supporting",
]


class EvidenceResponse(BaseModel):
    id: str
    profile_id: str
    category: EvidenceCategory
    original_filename: str
    mime_type: str
    storage_path: str
    status: str