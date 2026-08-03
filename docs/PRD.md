# Product Requirements Document

## 1. Document control

| Field | Value |
| --- | --- |
| Product | E-commerce Growth Agent |
| Version | 0.2 |
| Status | Product-validation MVP |
| Primary user | Owner or operations lead in a small e-commerce team |
| Data policy | Synthetic data in the public edition |

## 2. Problem statement

Small e-commerce teams often review sales, traffic, advertising and stock in separate spreadsheets. Analysis is repeated manually, recommendations vary by operator and important risks may be discovered too late.

## 3. Product hypothesis

If operating data is validated, calculated and reviewed through one explainable workflow, an operator can identify priority issues faster and make more consistent decisions without giving an autonomous system permission to change campaigns, prices or inventory.

This hypothesis has not yet been validated with a controlled user pilot. The public project therefore separates assumptions from measured outcomes.

## 4. Users and jobs to be done

### Primary user: operations lead

- review daily business health;
- identify which SKU requires attention;
- understand why a metric is abnormal;
- assign an action to advertising, product operations or supply chain;
- preserve evidence for a review meeting.

### Secondary user: business owner

- understand revenue, profit and risk without reading multiple spreadsheets;
- approve high-impact actions;
- compare outcomes after an intervention.

## 5. MVP scope

### In scope

1. Upload a CSV using a documented schema.
2. Validate required fields and funnel invariants.
3. Calculate GMV, orders, CTR, conversion, ad ROI and contribution profit.
4. Aggregate metrics by SKU.
5. Detect low CTR, low conversion, low ad ROI, negative contribution and stock risk.
6. Show evidence and prioritized recommendations.
7. Record an agent execution trace.
8. Require human approval before any external business action.

### Out of scope

- automatic changes to advertising platforms;
- automatic purchase orders or price changes;
- financial accounting or statutory reporting;
- demand forecasting;
- production authentication and role-based access;
- model-generated claims without source evidence.

## 6. Functional requirements

| ID | Requirement | Priority | Acceptance criterion |
| --- | --- | --- | --- |
| FR-01 | Import CSV | Must | A valid file produces a report without external network access. |
| FR-02 | Validate data | Must | Missing fields and invalid funnel values produce a clear error. |
| FR-03 | Calculate KPIs | Must | Metrics match independently calculated expected values. |
| FR-04 | Diagnose SKU risks | Must | Each finding contains severity, code, evidence and action. |
| FR-05 | Prioritize actions | Must | Critical findings appear before high and medium findings. |
| FR-06 | Show execution trace | Should | User can see which tools were executed and why. |
| FR-07 | Export JSON | Should | CLI writes a structured report when an output path is provided. |
| FR-08 | Configure thresholds | Must | User can load validated guardrails and the report preserves their effective values. |

## 7. Non-functional requirements

- **Explainability:** all findings must show the metric and threshold used.
- **Privacy:** public and demonstration datasets must not contain personal or confidential data.
- **Cost:** the MVP must run without a paid model API.
- **Performance:** a 10,000-row CSV should complete within five seconds on a normal laptop in a future benchmark.
- **Reliability:** calculation rules must be covered by automated tests.
- **Safety:** the product must not execute external commercial actions in v0.1.

## 8. Core user flow

1. User prepares or downloads a CSV.
2. User uploads the file.
3. System validates schema and values.
4. Agent selects deterministic analysis tools.
5. System calculates portfolio and SKU metrics.
6. System applies explicit diagnostic guardrails.
7. User reviews evidence and recommended actions.
8. User approves, rejects or delegates an action outside the MVP.

## 9. Product metrics

### Adoption

- percentage of invited operators who complete a first analysis;
- weekly active analysts;
- analyses per active user.

### Task outcome

- median time from data upload to priority issue identification;
- percentage of findings accepted by a human reviewer;
- false-positive rate by finding type;
- percentage of recommendations assigned to an owner.

### System quality

- successful import rate;
- calculation accuracy against test cases;
- analysis latency;
- error rate.

## 10. Risks

| Risk | Mitigation |
| --- | --- |
| Thresholds do not fit the business | Make thresholds configurable and validate them in a pilot. |
| Data is incomplete or stale | Display data range and validation warnings. |
| User treats advice as an automatic decision | Require approval and preserve evidence. |
| Confidential data enters a public demo | Use synthetic data and display an explicit warning. |
| A future LLM invents explanations | Generate only from structured findings and require citations. |

## 11. Release plan

- **v0.1:** offline product-validation MVP;
- **v0.2:** threshold configuration in the CLI and static prototype;
- **v0.3:** reproducible synthetic evaluation fixture and rule-coverage report;
- **v0.4:** API and persisted analysis history;
- **v0.5:** evidence-constrained explanation layer;
- **v0.6:** permissions, audit logs and controlled integrations;
- **v1.0:** measured pilot and production-readiness review.
