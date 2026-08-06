# System Architecture

## Design goals

- zero paid runtime dependency for the public MVP;
- explainable calculations and findings;
- separation between analysis and presentation;
- human approval for external actions;
- clear path from prototype to a controlled service.

## Logical architecture

```mermaid
flowchart TB
    subgraph Presentation
      W[Static web prototype]
      C[Command-line interface]
    end
    subgraph Application
      A[GrowthAgent orchestrator]
      T1[Input validation tool]
      T2[Metrics tool]
      T3[SKU aggregation tool]
      T4[Diagnosis tool]
      T5[Recommendation tool]
      CFG[Validated business guardrails]
      H[Bounded history store]
    end
    subgraph Data
      CSV[CSV input]
      JSON[Structured JSON report]
      HIST[Safe summary history JSON]
    end
    CSV --> W
    CSV --> C
    CFG --> W
    CFG --> C
    C --> A
    A --> T1 --> T2 --> T3 --> T4 --> T5
    A --> JSON
    JSON --> H --> HIST
```

The browser prototype mirrors the Python domain logic for a zero-setup demonstration. The Python package is the reference implementation for validation and testing.

## Component responsibilities

| Component | Responsibility |
| --- | --- |
| `domain.py` | Parse and validate input rows. |
| `config.py` | Validate, load and serialize business review guardrails. |
| `tools.py` | Perform calculations, diagnosis and recommendation construction. |
| `agent.py` | Select tools in a controlled sequence and preserve a trace. |
| `cli.py` | Provide a local execution interface and JSON export. |
| `history.py` | Fingerprint source data and persist only bounded, data-minimized summary records. |
| `site/` | Demonstrate the product experience without a server. |

## Future service architecture

```mermaid
flowchart LR
    U[Browser] --> API[FastAPI service]
    API --> Q[Job queue]
    Q --> A[Agent worker]
    A --> DB[(PostgreSQL)]
    A --> OBJ[(Object storage)]
    A --> LLM[Optional LLM adapter]
    API --> OBS[Logs, metrics and traces]
    A --> OBS
```

### Production decisions still required

- tenant and role model;
- deployment location and data residency;
- encrypted object storage;
- retention and deletion policy;
- idempotency for repeated uploads;
- queue, retry and timeout policy;
- model provider, budget and fallback;
- audit logging and incident response.

## Optional LLM boundary

A model may later:

- rewrite structured findings into plain language;
- answer questions using only the calculated report;
- summarize approved actions.

A model must not:

- calculate financial metrics when deterministic code is available;
- invent missing data;
- execute campaign, pricing or procurement actions without approval;
- receive secrets or personal information in prompts.

## Current local persistence boundary

The v0.4 history store retains summary KPIs, finding codes, counts, the source filename and a SHA-256 data fingerprint. It excludes uploaded rows and order/customer-level details. Its default 90-day and 20-record limits are enforced on every append. The JSON file has no authentication, encryption or tamper evidence and is not presented as a production database.
