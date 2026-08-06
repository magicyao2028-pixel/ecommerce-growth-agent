# Security and Governance

## Public portfolio controls

- sample data is synthetic;
- no API keys are required;
- no data is sent from the browser prototype;
- `.env` files are excluded from Git;
- the product never executes external commercial actions.
- optional history persists only summary fields and a data fingerprint, never uploaded source rows;
- local history defaults to 90 days and 20 records, with pruning on append.

## Production threat areas

### Data privacy

- classify uploaded data before processing;
- remove personal identifiers that are not necessary;
- encrypt data in transit and at rest;
- define retention and deletion periods;
- isolate tenants and business units.

### Authentication and authorization

- use enterprise identity where available;
- apply least privilege;
- separate viewer, analyst, approver and administrator roles;
- audit uploads, report access and approvals.

### Model and agent safety

- treat uploaded text as untrusted content;
- prevent prompt injection from expanding tool permissions;
- allowlist tools and arguments;
- set timeouts, rate limits and cost limits;
- require approval for price, campaign, inventory and customer-facing actions;
- preserve model, prompt and tool traces for review.

### Reliability

- validate file size and type;
- make repeated operations idempotent;
- use bounded retries;
- provide a fallback when a model or external service is unavailable;
- monitor latency, errors, tool failures and cost.

## Security release gate

Before production, require a documented architecture review, data classification, access-control test, secret scan, dependency scan, backup-and-restore test and incident response owner.

The current local JSON history is not encrypted, authenticated or tamper-evident. Operators must store it in an access-controlled location and delete it when the analysis purpose ends.
