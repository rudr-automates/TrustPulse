# TrustPulse Architecture

## Target Architecture

Borrower
?
Next.js / React
?
FastAPI
?
PostgreSQL
Cloud Object Storage
Cloud AI

## Components

### Frontend
Next.js / React

Responsibilities:
- borrower experience
- bilingual interface
- evidence upload
- analysis presentation
- Trust Profile
- Financial Resume
- Decision Card

### Backend
FastAPI / Python

Responsibilities:
- API
- authentication/session handling as required
- profile management
- evidence processing
- validation
- triangulation
- deterministic scoring
- recommendations
- Financial Resume generation
- Decision Card generation

### Database
PostgreSQL

Persistent application data only.

### Storage
Cloud object storage

Persistent user documents and other application files.

### AI
Cloud AI API

AI performs:
- document understanding
- classification
- structured extraction
- interpretation
- cross-document understanding
- explanation
- recommendations

AI does not directly determine the Trust Score.

### Scoring
Deterministic rules-based engine.

Trust dimensions:

- Repayment Reliability — 30%
- Payment Discipline — 25%
- Business Continuity — 25%
- Income & Sales Capacity — 20%

Trust Score:
0–100

Confidence Score:
0–100

Trust and Confidence are separate concepts.
