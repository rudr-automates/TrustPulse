import json
from functools import lru_cache

from google import genai
from google.genai import types

from backend.app.core.config import get_settings


SYSTEM_INSTRUCTION = """
You are the document analysis engine for TrustPulse.

Your task is to analyze a financial or supporting document and return
ONLY valid JSON matching the requested structure.

You must:

1. Identify the document type.
2. Identify the document title when available.
3. Extract only explicit facts visible in the document.
4. Never invent missing information.
5. Assess signs of possible editing, manipulation, or AI-generated content.
6. Clearly distinguish uncertainty from suspicious indicators.

You are NOT performing legal or forensic authentication.

Possible authenticity statuses:

- no_significant_indicators
- potential_manipulation
- inconclusive

Never claim guaranteed authenticity.
Never claim guaranteed fraud detection.
"""


@lru_cache
def get_gemini_client() -> genai.Client:
    settings = get_settings()

    return genai.Client(
        api_key=settings.ai_api_key,
    )


def analyze_document(
    file_bytes: bytes,
    mime_type: str,
) -> dict:
    settings = get_settings()
    client = get_gemini_client()

    document_part = types.Part.from_bytes(
        data=file_bytes,
        mime_type=mime_type,
    )

    prompt = """
Analyze this document and return JSON using exactly this structure:

{
  "document_type": string | null,
  "document_title": string | null,
  "facts": {
    "name": string | null,
    "date": string | null,
    "amount": number | null,
    "currency": string | null,
    "reference_number": string | null,
    "repayment_details": object | null,
    "payment_details": object | null,
    "business_details": object | null,
    "income_details": object | null,
    "tax_details": object | null
  },
  "authenticity": {
    "status": "no_significant_indicators" | "potential_manipulation" | "inconclusive",
    "confidence": number,
    "indicators": [string]
  }
}

Rules:

- Only use facts explicitly visible in the document.
- Use null when information is not available.
- Do not guess.
- Confidence must be between 0 and 100.
- Keep indicators concise and evidence-based.
- Do not make legal or forensic authentication claims.
"""

    try:
        response = client.models.generate_content(
            model=settings.ai_model,
            contents=[
                document_part,
                prompt,
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )
    except Exception as exc:
        raise RuntimeError(
            f"Gemini API request failed: {exc}"
        ) from exc

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Gemini returned invalid JSON: {response.text[:500]}"
        ) from exc