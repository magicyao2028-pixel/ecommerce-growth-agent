# Handoff

## Current state

- Release: v0.9.0
- Maintenance rounds completed: 8/10
- Runtime: offline Python 3.10+, no third-party runtime dependencies
- Public data: synthetic only
- Paid model calls: none
- External commercial actions: none

## Reproduce

```bash
python -m pip install -e .
growth-agent data/sample_sales.csv --explain --generated-at 2026-08-21T00:00:00+00:00 --output examples/sample_report_with_explanation.json
growth-agent-trial
python -m unittest discover -s tests -v
```

## M5 evidence

- the adapter context excludes uploaded source rows and the SKU metric table;
- explanation items cite declared finding and recommendation references;
- output carries the exact cited evidence, deterministic action, owner and approval boundary;
- unknown citations, unsupported numbers, automatic-action language and adapter exceptions trigger deterministic fallback;
- the adapter never recalculates metrics or executes an external action;
- the trial includes both a successful explanation and a synthetic unsafe-output probe.

## M6 evidence

- added a versioned offline service contract with request validation, optional thresholds and explanation inclusion;
- added an optional FastAPI adapter with `/health` and `/v1/analyze`, while keeping FastAPI/Uvicorn out of the default runtime dependencies;
- contract tests prove malformed requests fail closed and valid responses keep persistence, external actions and human approval explicit.

## M7 evidence

- the service returns a deterministic SHA-256 request receipt over validated rows, effective guardrails and explanation mode;
- generated timestamps are excluded so equivalent retries can be compared;
- the receipt is trace metadata only: no payload persistence or distributed deduplication is performed.

## M8 evidence

- added a deterministic reducer for caller-supplied, already-redacted request telemetry;
- validates unique request IDs, finite non-negative latency, status/error-code consistency and non-empty fixtures;
- reports request/error counts, error rate and min/average/max/p95 latency for reviewer comparison;
- explicitly records review-only operation with no persistence, monitoring-service call or external action;
- trial and unit tests cover the summary and its fail-closed validation paths.

## Next planned round

M9 should improve the service contract or reviewer evidence without adding authentication claims, shared persistence, distributed coordination or production deployment. Those remain later work.
