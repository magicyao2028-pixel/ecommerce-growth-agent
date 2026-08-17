# Handoff

## Current state

- Release stage: v0.5 trial-readiness prototype.
- Maintenance completed: M4/10.
- Core capability: offline KPI analysis, SKU diagnosis, prioritized actions, configurable guardrails and bounded local summary history.
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

## Next maintenance round

M5 should add an evidence-constrained explanation-adapter interface while preserving deterministic calculations and keeping the no-model default.

## Known limitations

- Browser and Python logic are mirrored manually and can diverge.
- Thresholds remain hypotheses until reviewed against a real, private dataset outside the public repository.
- The seven-case evaluation fixture is engineered regression evidence, not real-world precision evidence.
- Local history is single-user JSON, not a shared database or tamper-evident audit log.
- Duplicate suppression uses source filename plus data fingerprint; it is local idempotency, not distributed job coordination.
- There is no authentication, API service, or real user pilot.
