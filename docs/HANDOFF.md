# Handoff

## Current state

- Release: v0.6.0
- Maintenance rounds completed: 5/10
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

## Next planned round

M6 is a FastAPI service and contract-test boundary. It is not authorized by this handoff. Authentication, roles, shared persistence and production deployment remain later work.
