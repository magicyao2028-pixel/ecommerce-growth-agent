# Handoff

## Current state

- Release stage: v0.2 portfolio prototype.
- Maintenance completed: M1/10.
- Core capability: offline KPI analysis, SKU diagnosis, prioritized actions, and configurable guardrails.
- Public data: synthetic only.
- Runtime cost: zero paid API dependency.

## Verification command

```bash
python -m unittest discover -s tests -v
growth-agent data/sample_sales.csv --config config/business_thresholds.json --output report.json
```

## Next maintenance round

M2 should add a reproducible evaluation fixture and a small rule-coverage report. It should not add an LLM yet.

## Known limitations

- Browser and Python logic are mirrored manually and can diverge.
- Thresholds remain hypotheses until reviewed against a real, private dataset outside the public repository.
- There is no persistence, authentication, API service, or real user pilot.
