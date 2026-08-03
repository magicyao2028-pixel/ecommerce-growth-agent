# Handoff

## Current state

- Release stage: v0.3 portfolio prototype.
- Maintenance completed: M2/10.
- Core capability: offline KPI analysis, SKU diagnosis, prioritized actions, and configurable guardrails.
- Public data: synthetic only.
- Runtime cost: zero paid API dependency.

## Verification command

```bash
python -m unittest discover -s tests -v
growth-agent data/sample_sales.csv --config config/business_thresholds.json --output report.json
growth-agent-eval
```

## Next maintenance round

M3 should add local analysis history with explicit persistence and data-retention boundaries. It should not add an LLM yet.

## Known limitations

- Browser and Python logic are mirrored manually and can diverge.
- Thresholds remain hypotheses until reviewed against a real, private dataset outside the public repository.
- The seven-case evaluation fixture is engineered regression evidence, not real-world precision evidence.
- There is no persistence, authentication, API service, or real user pilot.
