# Evaluation Baseline

> Synthetic rule-isolation fixture. This is deterministic regression evidence, not a real-user study.

## Summary

| Metric | Result |
| --- | --- |
| Cases passed | 7/7 |
| Exact case match | 100% |
| Expected finding recall | 100% |
| Unexpected findings | 0 |
| Implemented rule coverage | 6/6 (100%) |

## Cases

| Case | Purpose | Result |
| --- | --- | --- |
| `HEALTHY_BASELINE` | Healthy operating signals produce no invented recommendation. | PASS |
| `LOW_CTR_ONLY` | Low click-through rate is isolated from conversion and profit risks. | PASS |
| `LOW_CONVERSION_ONLY` | Low click-to-order conversion is isolated. | PASS |
| `LOW_AD_ROI_ONLY` | Advertising ROI below the configured guardrail is isolated. | PASS |
| `NEGATIVE_CONTRIBUTION_ONLY` | Negative contribution after product and advertising cost is isolated. | PASS |
| `STOCKOUT_ONLY` | Estimated stock cover below seven days is isolated. | PASS |
| `OVERSTOCK_ONLY` | Estimated stock cover above 60 days is isolated. | PASS |

## Interpretation boundary

- The cases were designed to isolate the six implemented rules.
- Passing these cases shows reproducibility and regression coverage only.
- It does not prove real-world diagnostic precision, GMV growth, profit improvement, or user adoption.
