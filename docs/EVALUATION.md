# Evaluation Plan

## Objective

Evaluate whether the product calculates correctly, identifies useful risks and helps an operator reach a reviewable decision faster.

## Evaluation layers

### 1. Deterministic correctness

- KPI values match manually calculated fixtures;
- invalid schema and impossible funnel values are rejected;
- severity ordering is stable;
- the same input produces the same diagnosis.
- custom thresholds change only the relevant findings and are preserved in the output.

### 2. Diagnostic quality

Create a reviewed dataset with at least 50 SKU-period examples. Two experienced operators label whether each condition deserves attention.

Measure:

- precision by finding type;
- recall by finding type;
- false-positive rate;
- inter-reviewer agreement;
- percentage of recommendations accepted or modified.

### 3. User task study

Compare the existing spreadsheet process with the prototype for the same dataset.

Measure:

- time to identify the top three issues;
- number of calculation errors;
- confidence rating;
- usability feedback;
- quality of assigned actions.

### 4. Operational readiness

- latency for 1,000 and 10,000 rows;
- failed import rate;
- duplicate upload behavior;
- log completeness;
- access-control tests in a later service version.

## Initial test cases

| Case | Expected result |
| --- | --- |
| Missing `revenue` column | Reject with exact missing-field message. |
| Clicks exceed impressions | Reject as invalid funnel data. |
| Contribution profit below zero | Critical finding. |
| Conversion below 3% | High finding. |
| Stock cover below seven days | High stockout risk. |
| No guardrail breach | Empty findings list, not an invented recommendation. |
| Custom CTR threshold | Finding changes predictably and report records the supplied value. |

## Decision gate for v1.0

Do not claim business impact until a controlled pilot establishes a baseline and post-intervention result. A successful technical demo is not proof of saved labor, increased GMV or improved profit.
