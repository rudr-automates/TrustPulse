# Development Guide

## Development Principle

TrustPulse is cloud-first from the beginning.

Development occurs locally, but the architecture must never depend on the developer machine.

## Development Flow

inspect
? implement
? compile
? test
? diagnose
? fix
? retest

A feature is not complete merely because code was written.

## Completion Levels

1. Build passes
2. Unit/integration tests pass
3. End-to-end tests pass
4. Deployment passes

## Engineering Rules

- Prefer complete file replacements when a file is substantially affected.
- Do not make unnecessary micro-patches.
- Do not invent files, APIs, routes, tables, or architecture.
- Verify actual project state before modifying it.
- Keep Git history meaningful.
- Never commit secrets.
