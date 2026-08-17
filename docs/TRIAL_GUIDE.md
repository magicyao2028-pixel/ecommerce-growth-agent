# Reviewer Trial Guide

This is a 10–20 minute offline trial using synthetic data. It demonstrates a review workflow, not real GMV improvement or production deployment.

## Clean start

Requirements: Python 3.10 or later. No paid API, database, browser automation or external account is required.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
growth-agent-trial
python -m unittest discover -s tests -v
```

The trial command validates the machine-readable evidence index, screens the recorded external candidates, runs the synthetic CSV flow, verifies that all recommendations require human approval, exercises an invalid-funnel failure, and replays the synthetic duplicate-history feedback case.

## Expected result

- `reports/trial_report.json` reports `overall_passed: true`;
- eight synthetic rows produce all six implemented diagnostic codes;
- an impossible funnel row is rejected;
- an identical data-and-guardrail retry returns `duplicate_skipped`, while changed guardrails remain a distinct analysis;
- no external write or paid service is used.

## Recovery

- `ModuleNotFoundError`: activate the environment and rerun `python -m pip install -e .`.
- Missing evidence path: restore the referenced tracked file; do not edit the evidence index to hide a missing artifact.
- Changed diagnostic output: run the full tests and review guardrail changes before updating expected evidence.

## Do not adopt when

- the operator needs automatic campaign, price or inventory writes;
- source data cannot be reviewed and mapped to the documented CSV contract;
- role-based access, shared persistence or a tamper-evident audit log is mandatory;
- the business expects forecasting or causal GMV claims from this deterministic diagnostic prototype.

For a real pilot, add private-data handling review, named action owners, role controls, outcome definitions and a rollback plan. Human approval remains mandatory.
