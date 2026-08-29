# TrustPulse MVP Contracts

This document defines the MVP data, evidence, scoring, and API contracts.

These contracts must be treated as the source of truth for implementation.

---

# 1. User Profile

A borrower has one financial identity profile.

## Fields

- id
- auth_user_id
- full_name
- occupation
- years_in_business
- location
- language
- consent_accepted
- created_at
- updated_at

## Example

{
  "full_name": "Ramesh Kumar",
  "occupation": "Kirana Store Owner",
  "years_in_business": 6,
  "location": "Jaipur, Rajasthan",
  "language": "en"
}

---

# 2. Evidence

Evidence represents one uploaded financial document or supporting record.

## Evidence Categories

- repayment
- recurring_payment
- business
- income_sales
- tax
- asset
- supporting

## Supported File Types

- PDF
- JPG
- JPEG
- PNG
- DOCX

## Evidence States

- uploaded
- processing
- documented
- verified
- self_declared
- under_review
- low_quality
- not_verified
- unreadable
- duplicate

Unverified evidence must not automatically be treated as fraudulent.

---

# 3. Evidence Record

## Fields

- id
- profile_id
- category
- original_filename
- mime_type
- storage_path
- status
- uploaded_at
- analyzed_at

---

# 4. Extracted Facts

AI converts documents into structured facts.

## Possible Facts

- document_type
- document_title
- name
- date
- amount
- currency
- reference_number
- repayment_details
- payment_details
- business_details
- income_details
- tax_details

The AI output must be structured data.

The frontend must never depend on free-form AI text for scoring.

---

# 5. Validation Result

Each evidence item can have validation findings.

## Fields

- evidence_id
- document_quality
- name_consistency
- date_consistency
- amount_consistency
- period_consistency
- missing_fields
- duplicate_detected
- contradiction_detected
- corroboration_count
- validation_notes
- authenticity_status
- manipulation_indicators
- authenticity_confidence

### Authenticity Assessment

The MVP evaluates whether a submitted document shows signs of editing, manipulation, or AI-generated content.

This is an assessment, not forensic or legal authentication.

### Possible Results

#### No significant indicators detected

The system did not identify meaningful signs of manipulation.

#### Potential manipulation detected

The system identified one or more suspicious indicators.

#### Inconclusive

The available evidence is insufficient to make a confident authenticity assessment.

### Rules

- Never claim guaranteed authenticity.
- Never automatically classify an inconclusive document as fraudulent.
- Authenticity assessment must contribute to evidence confidence.
- Authenticity assessment must not directly determine Trust Score.

Validation findings affect confidence and signal quality.

They do not automatically mean fraud.

---

# 6. Financial Signals

Financial signals are the bridge between evidence and scoring.

## Core Dimensions

### Repayment Reliability

Weight: 30%

Examples:

- on-time repayments
- repayment completion
- missed repayments
- repayment consistency

### Payment Discipline

Weight: 25%

Examples:

- recurring bill consistency
- payment regularity
- continuity of recurring payments

### Business Continuity

Weight: 25%

Examples:

- supplier activity
- business invoices
- recurring business activity
- operating continuity

### Income & Sales Capacity

Weight: 20%

Examples:

- sales records
- income records
- payment records
- income consistency

---

# 7. Supporting Evidence

Tax and asset evidence are valid evidence types.

They are NOT separate core Trust dimensions.

They may:

- corroborate other evidence
- improve confidence
- strengthen the financial narrative
- help explain financial activity

They must not automatically create an independent score category.

---

# 8. Signal Calculation

Every financial signal is deterministic.

Conceptual formula:

signal_score =
base_signal
× quality_factor
× recency_factor
× corroboration_factor
− anomaly_penalty

All factors are normalized to predictable ranges.

The implementation must use explicit rules rather than an LLM-generated score.

---

# 9. Evidence Quality Factor

Evidence quality represents how usable the document is.

Example levels:

High quality → 1.00
Good quality → 0.85
Low quality → 0.60
Unreadable → 0.00

These values are implementation constants and must live in the scoring engine, not the frontend.

---

# 10. Recency

More recent evidence is generally more relevant to the current financial profile.

Recency must use deterministic rules.

Example:

Recent → full weight
Older → reduced weight
Very old → substantially reduced weight

The exact time bands must be implemented centrally and tested.

---

# 11. Corroboration

Independent evidence supporting the same activity increases confidence.

Example:

Repayment receipt
+
payment record
+
lender acknowledgement

is stronger than one repayment document alone.

Corroboration should increase confidence and may strengthen the relevant financial signal.

---

# 12. Contradictions

Contradictory evidence must reduce confidence.

Examples:

- conflicting names
- impossible date sequence
- inconsistent amounts
- conflicting business information
- overlapping records with incompatible facts

Contradictions must never be silently ignored.

---

# 13. Trust Score

Trust Score range:

0–100

Dimension weights:

- Repayment Reliability: 30%
- Payment Discipline: 25%
- Business Continuity: 25%
- Income & Sales Capacity: 20%

Only dimensions with meaningful evidence contribute to the Trust Score.

Missing evidence should not automatically be treated as poor financial behavior.

The score is normalized based on available weighted evidence.

---

# 14. Confidence Score

Confidence Score range:

0–100

Confidence measures how strongly the available evidence supports the assessment.

Confidence depends on:

- evidence coverage
- evidence quality
- corroboration
- consistency
- contradictions
- anomalies
- recency

A profile can therefore have:

High Trust + Low Confidence

or:

Moderate Trust + High Confidence

Trust and Confidence must remain separate.

---

# 15. AI Boundary

AI MAY:

- classify documents
- extract facts
- interpret evidence
- identify patterns
- compare documents
- explain findings
- generate recommendations

AI MUST NOT:

- invent evidence
- invent extracted facts
- directly assign Trust Score
- directly assign Confidence Score
- override deterministic scoring rules

The authoritative scoring engine is backend code.

---

# 16. Recommendations

Recommendations must be generated from the actual profile state.

Possible triggers:

- missing evidence
- weak dimensions
- poor corroboration
- low confidence
- inconsistent evidence
- useful additional supporting documents

Recommendations must be actionable.

Avoid generic motivational content.

---

# 17. Financial Resume

The Financial Resume represents the user's financial identity.

It should summarize:

- identity
- financial activity
- repayment behavior
- payment discipline
- business continuity
- income/sales evidence
- supporting evidence
- Trust Score
- Confidence
- positive indicators
- uncertainties
- recommendations

The Financial Resume is NOT simply:

Trust Score + Confidence.

---

# 18. Decision Card

The Decision Card is the final MVP output.

It is generated from the Financial Resume.

It contains:

- Applicant
- Trust
- Confidence
- Evidence breakdown
- Positive indicators
- Uncertainty
- Assessment
- Suggested next step

The Decision Card is NOT a loan approval.

---

# 19. API Contract

All backend APIs use JSON unless explicitly handling file transfer.

Base path:

/api/v1

## Profile

POST /profile

Create or update the borrower's financial identity.

GET /profile

Return the current borrower's profile.

---

## Evidence

POST /evidence

Create an evidence record and initiate upload processing.

GET /evidence

Return the borrower's evidence list.

GET /evidence/{id}

Return one evidence item and its current status.

POST /evidence/{id}/analyze

Start or retry document analysis.

---

## Trust Profile

GET /trust-profile

Return:

- Trust Score
- Confidence Score
- dimension breakdown
- evidence summary
- positive indicators
- uncertainties
- explanation
- recommendations

---

## Financial Resume

GET /financial-resume

Return the current Financial Resume.

---

## Decision Card

GET /decision-card

Return the current Decision Card.

---

# 20. API Principles

The backend is authoritative.

The frontend must not calculate:

- Trust Score
- Confidence Score
- dimension scores
- evidence validation
- triangulation

The frontend only displays backend results.

---

# 21. Example Trust Profile Response

{
  "trust_score": 76,
  "confidence_score": 83,
  "dimensions": {
    "repayment_reliability": 88,
    "payment_discipline": 81,
    "business_continuity": 74,
    "income_sales_capacity": 61
  },
  "evidence_summary": {
    "verified": 8,
    "documented": 7,
    "self_declared": 3
  },
  "positive_indicators": [],
  "uncertainties": [],
  "recommendations": []
}

These numbers are example output only.

They must never be hardcoded into the application.

---

# 22. MVP Demo Evidence Set

The controlled demo should support evidence such as:

- loan repayment receipt
- electricity/utility evidence
- supplier invoice
- tax-payment receipt
- sales/income record

The demo narrative should be able to surface evidence such as:

- 10/10 repayments
- 11 months recurring bills
- 8 months supplier activity
- tax evidence detected
- 3 independent sources supporting ongoing business activity

These are demo-story targets, not hardcoded scoring outputs.

---

# 23. Contract Rule

If implementation conflicts with this document:

1. Stop.
2. Identify the conflict.
3. Resolve the contract first.
4. Update this document.
5. Commit the change.
6. Then continue implementation.

Do not silently change the product contract inside application code.