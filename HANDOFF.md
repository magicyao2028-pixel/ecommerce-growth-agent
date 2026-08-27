# Handoff

## Current state

- Release stage: v0.8 trial-readiness prototype.
- Maintenance completed: M7/10.
- Core capability: offline KPI analysis, SKU diagnosis, prioritized actions, configurable guardrails, bounded local summary history, a governed explanation boundary and a versioned service contract with deterministic retry receipts.
- Public data: synthetic only.
- Runtime cost: zero paid API dependency.

## Verification command

```bash
python -m unittest discover -s tests -v
growth-agent data/sample_sales.csv --config config/business_thresholds.json --output report.json
growth-agent data/sample_sales.csv --history output/analysis_history.json --history-retain-days 90 --history-max-records 20
growth-agent-eval
growth-agent-trial
```

## Maintenance completed in M5-M7

- M5: evidence-constrained explanation adapter with deterministic fallback.
- M6: versioned offline service contract and optional FastAPI adapter.
- M7: deterministic request receipt for retry tracing; timestamps are excluded from the fingerprint and no persistence or distributed deduplication is claimed.

## Next maintenance round

M8 should add a small, testable request-observability summary (latency/error fields supplied by the caller) while preserving the offline, no-write boundary.

## Known limitations

- Browser and Python logic are mirrored manually and can diverge.
- Thresholds remain hypotheses until reviewed against a real, private dataset outside the public repository.
- The seven-case evaluation fixture is engineered regression evidence, not real-world precision evidence.
- Local history is single-user JSON, not a shared database or tamper-evident audit log.
- Duplicate suppression uses source filename plus data and effective-guardrail fingerprints; it is local idempotency, not distributed job coordination.
- The optional API adapter has no authentication, shared persistence, queue, or real user pilot.
- Request receipts are deterministic trace metadata only; they do not coordinate retries across processes or instances.
