# System Tables Audit Logs — DAB Support

## What This Is

A fork of the existing `system-tables-audit-logs` repo that adds a Databricks Asset Bundle (DAB) deployment path for Alerts v2. The DAB path dynamically generates Alerts v2 resources (with inline SQL and native scheduling) from the existing `resources/queries_and_alerts.json` file, sitting alongside the repo's original notebook and Terraform deployment paths. Open-source users (SAs, customers, Databricks employees) can clone the repo and run `databricks bundle deploy` to provision audit-log alerts on their own workspace.

## Core Value

Deploy audit-log Alerts v2 from JSON via a single `databricks bundle deploy` — and have a real alert fire on real audit-log data.

## Requirements

### Validated

<!-- Capabilities already shipped in the existing repo; these stay intact. -->

- ✓ JSON config (`resources/queries_and_alerts.json`) is the single source of truth for queries and alert definitions — existing
- ✓ Notebook path creates SQL queries and alerts via the Databricks SDK — existing
- ✓ Terraform path provisions queries, alerts, SQL warehouse, and a scheduled job — existing
- ✓ Optional geolocation UDF (`notebooks/geolocation_function_and_queries.sql`) enriches audit queries with IP → country data — existing

### Active

<!-- New scope for the DAB support milestone. All hypotheses until shipped and validated end-to-end. -->

- [ ] DAB deployment path coexists with the notebook and Terraform paths in this repo
- [ ] Dynamic Python generator reads `resources/queries_and_alerts.json` and emits Alerts v2 resources at bundle evaluation time
- [ ] Alerts v2 resources use inline SQL (no separate query resources) and native Alerts v2 scheduling (no separate job resource)
- [ ] Email notifications are wired from bundle variables (recipient list) into each generated alert
- [ ] Bundle **template** is committed to the repo (parameterized, generic, safe to share)
- [ ] Real bundle **instance** (with real workspace host, emails, etc.) deploys to the developer's `dev` target but is gitignored
- [ ] End-to-end validation: at least one deployed alert actually fires on real `system.access.audit` data and emails the configured recipient

### Out of Scope

<!-- Explicit exclusions with reasoning, so they don't creep back in. -->

- Slack, PagerDuty, or generic webhook notifications — email is sufficient for v1; add later if asked
- Replacing or removing the notebook path — users still want the interactive/ad-hoc deploy option
- Replacing or removing the Terraform path — keep for users already standardized on Terraform
- Separate Databricks SQL Query resources — Alerts v2 inline SQL makes standalone queries unnecessary for this path
- Separate scheduled Job resource for alert refresh — Alerts v2 has native scheduling
- Migrating the geolocation UDF to DAB — out of scope for v1; stays in the notebook path

## Context

**Existing repo state (from `.planning/codebase/`):**

- Python 3.x notebook entry point `notebooks/create_queries_and_alerts.py` uses `DatabricksSQLHelper` (in `notebooks/functions.py`) to call the Databricks SDK.
- Terraform module under `terraform/` (main.tf, sql.tf, job.tf) provisions directories, queries, alerts, SQL warehouse, and a 1-hour cron job.
- Config file `resources/queries_and_alerts.json` defines each query's name, description, SQL text, parent directory, and optional alert sub-object (operator, threshold, custom message).
- `databricks-sdk` version is unpinned in `requirements.txt`; Terraform provider pinned `>= 1.59.0, < 2.0.0`.
- Known tech debt (from CONCERNS.md): no schema validation on the JSON, no unit tests, duplicate logic between the notebook and Terraform paths, brittle HTML-string generation, sequential SDK calls.

**Alerts v2 context:**

- Databricks recently introduced Alerts v2, which embeds the SQL inline and includes native scheduling — eliminating the need for paired Query + Alert + Job resources.
- Alerts v2 is supported natively by DAB (the current Terraform/notebook paths do not leverage it).
- The exact v2 resource shape (field names, schedule syntax, notification block) needs to be confirmed in the research phase before plans are written.

**Deployment model:**

- **Template bundle:** committed, parameterized (workspace host, emails, catalog/schema if needed, warehouse ID) so any user can clone, fill in variables, and deploy.
- **Real instance:** copy of the template with real values for the developer's own account; gitignored to avoid committing secrets or personal workspace URLs.

## Constraints

- **Tech stack:** Must use Databricks Asset Bundles (DAB) and Alerts v2 — those are the whole point of this milestone.
- **Compatibility:** Existing notebook and Terraform paths must keep working; no breaking changes to `resources/queries_and_alerts.json` that would regress them (additive fields are fine).
- **Dependencies:** Databricks CLI version must support Alerts v2 bundle resources — exact minimum version to be confirmed in research.
- **Security:** Real bundle instance and any alert-recipient emails must not be committed to git.
- **Distribution:** Repo is (or will be) open source — the committed template must be generic, documented, and safe for strangers to clone.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Add DAB path alongside notebook + Terraform (not replace) | Users on existing paths shouldn't be forced off; DAB is the new primary for v2 | — Pending |
| Dynamic Python resource generation, not static YAML | JSON is the existing single source of truth; manual YAML drift is the exact problem this avoids | — Pending |
| Alerts v2 with inline SQL, no standalone Query resources | Matches Alerts v2 model; avoids duplication across Query + Alert | — Pending |
| Native Alerts v2 scheduling, no separate bundle Job | v2 has it built-in; one less resource to manage | — Pending |
| Email-only notifications for v1 | Matches current behavior; Slack/PD can come later | — Pending |
| Commit the template bundle; gitignore the real instance | Lets users fork the template without leaking the author's workspace details | — Pending |

---
*Last updated: 2026-04-24 after initialization*
