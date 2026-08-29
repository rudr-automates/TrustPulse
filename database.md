# TrustPulse Database

## Core Tables

- profiles
- evidence
- extracted_facts
- validation_results
- evidence_relations
- financial_signals
- assessments
- recommendations
- financial_resumes
- decision_cards

## Data Flow

profiles
→ evidence
→ extracted_facts
→ validation_results
→ evidence_relations
→ financial_signals
→ assessments
→ recommendations
→ financial_resumes
→ decision_cards

## Principles

- Uploaded files live in cloud object storage.
- PostgreSQL stores structured application data and metadata.
- AI output is stored as structured data.
- Trust Score is calculated by deterministic backend rules.
- Confidence is calculated separately.
- Evidence ownership is tied to the borrower profile.
- Financial evidence must not be publicly accessible.