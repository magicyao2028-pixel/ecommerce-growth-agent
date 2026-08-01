# Business Workflow

## Current-state hypothesis

```mermaid
flowchart LR
    A[Export store data] --> B[Open several spreadsheets]
    B --> C[Calculate metrics manually]
    C --> D[Identify suspected issues]
    D --> E[Discuss in chat or meeting]
    E --> F[Assign actions informally]
    F --> G[Limited outcome tracking]
```

Observed problems must be validated with real users before a pilot. Likely issues include duplicated calculation, inconsistent thresholds, missing ownership and weak traceability.

## Proposed workflow

```mermaid
flowchart TD
    A[Operator uploads CSV] --> B{Schema valid?}
    B -- No --> C[Show exact validation error]
    C --> A
    B -- Yes --> D[Calculate portfolio KPIs]
    D --> E[Aggregate by SKU]
    E --> F[Apply diagnostic guardrails]
    F --> G[Rank evidence-based actions]
    G --> H{Human approves action?}
    H -- No --> I[Reject or request more evidence]
    H -- Yes --> J[Assign action to responsible team]
    J --> K[Record outcome in future iteration]
```

## Responsibility swimlane

| Stage | Operator | Growth Agent | Business owner | Functional team |
| --- | --- | --- | --- | --- |
| Prepare data | Responsible | — | — | Consulted |
| Validate and calculate | Informed | Responsible | — | — |
| Review evidence | Responsible | Provides evidence | Accountable | Consulted |
| Approve high-impact action | Consulted | No authority | Accountable | Informed |
| Execute action | Informed | No authority | Accountable | Responsible |
| Review outcome | Responsible | Future analysis | Accountable | Consulted |

## Why a workflow before an autonomous agent

The sequence is predictable and business actions can affect money and inventory. A controlled workflow is safer than allowing a model to choose and execute actions autonomously. The “agent” in this MVP orchestrates analysis tools and prioritizes findings, while authority remains with a human.
