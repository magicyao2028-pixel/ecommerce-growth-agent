# E-commerce Growth Agent

[![CI](https://github.com/magicyao2028-pixel/ecommerce-growth-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/magicyao2028-pixel/ecommerce-growth-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> 中文介绍：这是一个面向中小电商企业的离线经营分析与决策辅助原型。它将销售、流量、广告和库存数据转化为经营指标、风险诊断和行动建议，完整展示需求分析、PRD、业务流程、系统架构、接口规范、测试、评测与迭代设计。公开版本仅使用合成数据，不包含任何公司或客户隐私。

**Live prototype:** https://magicyao2028-pixel.github.io/ecommerce-growth-agent/

## Project context

This portfolio edition documents an AI application and product practice explored in the business context of **Changsha Shiju Trading Co., Ltd.** It is designed to show how an operational problem can be converted into a testable product, rather than presenting a model-call demo as a finished commercial system.

## Business problem

Small e-commerce teams often review traffic, orders, advertising and inventory in separate spreadsheets. The process is slow, difficult to standardize and dependent on individual experience. This project provides one decision workspace that:

- calculates GMV, conversion, ROI and contribution profit;
- detects traffic, conversion, advertising and stock risks by SKU;
- prioritizes actions with explicit evidence;
- keeps a visible execution trace for review;
- works offline and does not require a paid model API.

## What this repository demonstrates

| Capability | Evidence |
| --- | --- |
| Product discovery | [PRD](docs/PRD.md) and documented assumptions |
| Process design | [Business flow](docs/BUSINESS_FLOW.md) |
| Technical design | [Architecture](docs/ARCHITECTURE.md) and [OpenAPI specification](docs/openapi.yaml) |
| Agent workflow | Explicit tool selection, execution trace and recommendation prioritization |
| Product validation | Unit tests, evaluation cases and acceptance criteria |
| Security thinking | Offline-first design, synthetic data and human approval boundaries |
| User-facing prototype | Zero-cost static web application in [`site/`](site/) |

## Architecture

```mermaid
flowchart LR
    U[Commerce operator] --> I[CSV ingestion]
    I --> V[Schema validation]
    V --> O[Growth agent orchestrator]
    O --> M[Metrics tool]
    O --> D[Diagnosis tool]
    O --> R[Recommendation tool]
    M --> P[Structured report]
    D --> P
    R --> P
    P --> H[Human review]
```

The current MVP is deliberately deterministic and offline. This makes every recommendation traceable and keeps the project free to run. A future LLM adapter may explain structured findings, but it must not replace metric calculation or human approval.

## Quick start

Requirements: Python 3.10 or later. No third-party runtime dependency is required.

```bash
python -m pip install -e .
growth-agent data/sample_sales.csv --output report.json
growth-agent data/sample_sales.csv --config config/business_thresholds.json --output report.json
python -m unittest discover -s tests -v
```

To view the prototype locally, open `site/index.html` or serve the folder:

```bash
python -m http.server 8000 --directory site
```

Then visit `http://localhost:8000`.

## Input data

The CSV schema is intentionally simple:

```text
date,sku,product_name,category,impressions,clicks,orders,units,revenue,ad_spend,cost,stock
```

All monetary values are assumed to use the same currency. The sample file contains synthetic data.

## Output

The agent returns:

- portfolio-level KPI summary;
- SKU-level diagnostic findings;
- prioritized operational recommendations;
- a transparent execution trace;
- warnings when data or assumptions are incomplete.

## Product boundaries

This is a product-validation MVP, not a production ERP or advertising platform. It does not automatically change prices, pause campaigns, place purchase orders or publish content. High-impact actions require human confirmation.

## Configurable business guardrails

The default review thresholds are visible in [`config/business_thresholds.json`](config/business_thresholds.json). Operators can supply a JSON file through `--config`; the report preserves the effective values so a reviewer can reproduce why a finding appeared. The static prototype exposes the same five guardrails for an immediate what-if comparison.

## Documentation

- [Product requirements document](docs/PRD.md)
- [Business workflow](docs/BUSINESS_FLOW.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Evaluation plan](docs/EVALUATION.md)
- [Security and governance](docs/SECURITY.md)
- [中文项目说明](docs/PRODUCT_PORTFOLIO_CN.md)
- [OpenAPI specification](docs/openapi.yaml)

## Roadmap

- v0.1: offline metrics, diagnosis, recommendations and static prototype;
- v0.2: configurable business guardrails in the CLI and static prototype;
- v0.3: FastAPI service and persisted analysis history;
- v0.4: optional model-generated explanation with evidence constraints;
- v0.5: role-based access and audit logs;
- v1.0: controlled pilot with real users and measured operational outcomes.

## License

MIT License. See [LICENSE](LICENSE).
