# TrustPulse Architecture

## 1. Product Architecture

TrustPulse is a borrower-first financial identity builder.

The MVP flow is:

Borrower
→ Financial Identity
→ Evidence Vault
→ AI Evidence Analysis
→ Trust Profile
→ Financial Resume
→ Decision Card

The MVP ends at the Decision Card.

---

## 2. High-Level System Architecture

Borrower
    ↓
Next.js / React Frontend
    ↓ HTTPS
FastAPI Backend
    ↓
┌───────────────┬────────────────┬─────────────────┐
│               │                │                 │
▼               ▼                ▼                 ▼
PostgreSQL   Cloud Storage    Cloud AI API     Auth
│               │                │                 │
▼               ▼                ▼                 ▼
Profiles      Evidence        Extraction       User
Evidence      Documents       Interpretation    Identity
Signals
Scores
Resume
Decision Card

---

## 3. Frontend

Technology:

- Next.js
- React
- TypeScript
- Tailwind CSS

Responsibilities:

- Financial Identity interface
- Evidence Vault
- Evidence upload
- Evidence status display
- AI Evidence Analysis interface
- Trust Profile
- Trust Score presentation
- Confidence presentation
- Recommendations
- Financial Resume
- Decision Card
- English/Hindi interface
- Consent and privacy controls

The frontend must not contain the authoritative scoring logic.

---

## 4. Backend

Technology:

- Python
- FastAPI

Responsibilities:

- API endpoints
- Profile management
- Evidence metadata
- Secure upload coordination
- Document processing orchestration
- AI integration
- Evidence validation
- Evidence comparison
- Triangulation
- Financial signal generation
- Deterministic scoring
- Confidence calculation
- Recommendations orchestration
- Financial Resume generation
- Decision Card generation

The backend is the authoritative application/business-logic layer.

---

## 5. Database

Technology:

PostgreSQL

The database stores structured application data such as:

- User/profile information
- Evidence metadata
- Extracted evidence facts
- Validation results
- Evidence relationships
- Financial signals
- Trust scores
- Confidence scores
- Recommendations
- Financial Resume data
- Decision Card data

The database does NOT store persistent uploaded files directly.

---

## 6. Object Storage

Technology:

Cloud object storage.

MVP implementation:

Supabase Storage.

Persistent user documents are stored in private cloud storage.

Examples:

- PDF documents
- JPG/JPEG images
- PNG images
- DOCX documents

The database stores metadata and references to those objects.

There is no permanent local upload directory.

Temporary request-scoped files may be used during document processing when required.

---

## 7. Authentication

MVP implementation:

Supabase Auth.

Authentication exists to establish a user-owned financial profile and protect access to evidence.

The application must not expose one borrower's evidence or profile to another borrower.

---

## 8. AI Layer

Technology:

Cloud AI API.

MVP provider:

Google Gemini API.

AI responsibilities:

- Document understanding
- Document classification
- Structured extraction
- Interpretation
- Cross-document understanding
- User-facing explanations
- Recommendations

AI produces structured evidence interpretation.

AI does NOT directly determine the Trust Score.

---

## 9. Document Processing Pipeline

Evidence
    ↓
Document ingestion
    ↓
OCR / text extraction
    ↓
Information extraction
    ↓
Structured evidence
    ↓
Validation
    ↓
Comparison
    ↓
Triangulation
    ↓
Financial signals
    ↓
Deterministic scoring
    ↓
Trust + Confidence
    ↓
Explanation
    ↓
Financial Resume
    ↓
Recommendations
    ↓
Decision Card

OCR and document-processing dependencies must be deployable in the eventual cloud environment.

No hardcoded machine-specific executable paths are permitted.

---

## 10. Deterministic Scoring Engine

The Trust Score is calculated by backend rules.

Core dimensions:

### Repayment Reliability
Weight: 30%

### Payment Discipline
Weight: 25%

### Business Continuity
Weight: 25%

### Income & Sales Capacity
Weight: 20%

Trust Score:

0–100

Confidence Score:

0–100

Trust and Confidence are separate measurements.

Tax evidence and asset evidence are supported evidence categories but are not automatically separate core scoring dimensions.

---

## 11. Evidence Integrity

The system should support:

- Duplicate detection
- Name consistency checks
- Date consistency checks
- Amount consistency checks
- Period consistency checks
- Missing-field detection
- Document-quality assessment
- Corroboration
- Contradiction detection
- Confidence reduction

Unverified evidence must not automatically be treated as fraudulent.

The system communicates uncertainty rather than claiming guaranteed fraud detection.

---

## 12. Triangulation

Core principle:

One document suggests.

Multiple independent pieces of evidence corroborate.

Example:

Repayment evidence
+
Utility payment history
+
Supplier activity

can collectively provide stronger support for financial reliability than any single document alone.

The system should communicate this in borrower-friendly language.

Example:

"We found 3 records that support the same financial activity."

---

## 13. Trust vs Confidence

Trust represents:

How strong the observed financial-reliability signals are.

Confidence represents:

How strongly the available evidence supports the assessment.

A high Trust Score does not automatically mean high Confidence.

Insufficient, contradictory, low-quality, or poorly corroborated evidence can reduce Confidence.

---

## 14. Language

MVP languages:

- English
- Hindi

The language selector remains available throughout the application.

Use a centralized i18n/translation dictionary.

Do not scatter hardcoded user-facing strings throughout components.

The following must be localized:

- Navigation
- Buttons
- Labels
- Instructions
- Evidence categories
- Analysis messaging
- Score explanations
- Recommendations
- Warnings
- Decision Card text
- Help text

---

## 15. Privacy

Financial documents are sensitive.

The MVP must support:

- User consent
- Controlled uploads
- Private cloud storage
- User-owned profiles
- Limited data collection
- Evidence deletion
- No unnecessary surveillance

Do not claim "bank-grade security" unless the relevant controls have actually been implemented and tested.

---

## 16. Deployment Architecture

Target deployment:

Frontend:
Vercel

Backend:
Cloud-hosted FastAPI service

Database:
Supabase PostgreSQL

Storage:
Supabase Storage

AI:
Cloud AI API

Source control:
GitHub

Development happens locally.

Production must not depend on the developer's PC.

---

## 17. Environment Configuration

All environment-specific configuration must use environment variables.

Examples:

- Database connection
- Storage credentials
- AI API credentials
- Authentication configuration
- API URLs
- Deployment configuration

Never commit real secrets.

Never hardcode:

- API keys
- Passwords
- Tokens
- Windows paths
- Production URLs

`.env.example` documents required configuration without containing real credentials.

---

## 18. Explicitly Out of MVP Architecture

The following are not required for the borrower MVP:

- Lender dashboard
- Bank dashboard
- Loan approval system
- Loan disbursement
- Direct banking integration
- Account Aggregator integration
- CIBIL replacement
- Real-world underwriting
- Continuous surveillance
- Cell tower tracking
- SIM behavior analysis
- Psychometric credit scoring
- ML credit prediction
- Mobile application
- Blockchain
- Unnecessary vector database infrastructure
- Unnecessary Redis infrastructure
- Multiple backend frameworks

These may be considered in a future architecture if justified by an actual product requirement.

---

## 19. Architectural Principles

### Cloud-first

The system is designed for cloud deployment from the beginning.

### AI interprets. Rules score.

AI provides structured interpretation.

Deterministic backend rules calculate Trust and Confidence.

### Evidence over assumptions

Scores must be explainable through evidence and signals.

### Trust and Confidence remain separate

The system must communicate uncertainty.

### Borrower-first

The MVP focuses entirely on helping the borrower build and understand their Financial Resume.

### Minimal necessary infrastructure

Every infrastructure component must have a clear MVP purpose.

### Reproducibility

A fresh developer environment should be able to reproduce the application without depending on the original developer machine.