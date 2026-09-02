# Changelog

## 1.0.0 - 2026-09-02

- added a response-envelope validator for reviewer and UI consumers;
- validated request-fingerprint shape, no-write declarations and human approval requirements;
- added fail-closed tests while preserving offline, synthetic and non-production boundaries.

## 0.9.0 - 2026-08-30

- Added a deterministic request-observability summary for caller-supplied redacted events.
- Added latency/error metrics, validation, synthetic fixture, trial evidence and no-monitoring-write checks.

## 0.8.0 - 2026-08-27

- Added a deterministic request receipt to the offline service contract.
- Excluded generated timestamps from the fingerprint so equivalent retries remain comparable.
- Added trial and unit regression coverage for stable fingerprints and explicit no-persistence/no-deduplication boundaries.

## 0.7.0 - 2026-08-25

- Added a versioned offline service contract for row validation, optional thresholds and explanation inclusion.
- Added an optional FastAPI adapter with `/health` and `/v1/analyze`; FastAPI and Uvicorn remain optional extras rather than default runtime dependencies.
- Added contract tests and explicit governance fields for authentication, persistence, external actions and human approval.
- Preserved the deterministic analysis core, source-row minimization and zero-production-write boundary.

## 0.6.0 - 2026-08-21

- Added an optional evidence-constrained explanation adapter interface.
- Limited adapter context to structured summary, findings and deterministic recommendations; source rows and SKU metric tables are excluded.
- Required known finding and recommendation references and preserved exact source evidence in every output item.
- Blocked unsupported numeric claims and automatic-action language.
- Added deterministic fallback for malformed output, unknown references, unsafe content and adapter exceptions.
- Extended the offline trial, evidence index, documentation and regression suite for the M5 boundary.

## 0.5.0 - 2026-08-17

- Added an executable reviewer trial and machine-readable evidence index.
- Recorded exact external component versions, licenses and non-adoption reasons without forcing dependencies.
- Converted a clearly synthetic duplicate-retry report into idempotent history behavior and a regression test.
- Kept identical data under different effective guardrails as distinct analysis records.
- Rejected non-finite business thresholds before analysis or JSON evidence generation.
- Rejected boolean guardrails plus non-finite, boolean and fractional sales metrics before KPI calculation.
- Made same-second analysis identifiers unique across source and effective-guardrail contexts.
- Added failure-path verification, trial instructions, honest non-adoption conditions and public trial evidence.

## 0.4.0 - 2026-08-06

- added optional local analysis-history persistence with a safe summary schema;
- added stable source-data fingerprints without retaining source rows;
- added configurable record-count and age-based retention limits;
- added five regression tests covering minimization, expiry, capacity and validation;
- documented the single-user persistence boundary in the CLI, architecture, security guidance and browser prototype.

## 0.3.0 - 2026-08-03

- added seven reproducible synthetic rule-isolation cases;
- added exact-match, expected-finding recall, false-positive and rule-coverage metrics;
- added deterministic JSON and Markdown evaluation reports;
- exercised all six implemented finding codes with 7/7 passing cases;
- documented why the baseline is not evidence of real-world precision or business impact.

## 0.2.0 - 2026-08-02

- added validated JSON business-threshold configuration;
- added CLI `--config` support and preserved effective guardrails in reports;
- added editable guardrails to the offline browser prototype;
- added tests for custom configuration and invalid ranges;
- added the ten-round maintenance plan and restart handoff.

## 0.1.0 - 2026-08-01

- published the offline e-commerce growth analysis prototype;
- added deterministic metrics, diagnosis, recommendations, tests, documentation, CI, and static demo.
