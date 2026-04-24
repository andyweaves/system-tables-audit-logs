# External Integrations

**Analysis Date:** 2026-04-24

## APIs & External Services

**Databricks APIs:**
- Databricks Workspace API
  - SDK: `databricks-sdk` (Python)
  - Used for: Creating SQL queries, alerts, directories, and managing workspace objects
  - Auth: `DATABRICKS_HOST`, `DATABRICKS_TOKEN` (env vars or Databricks CLI config)
  - Implementation: `notebooks/functions.py` lines 12-14, 21-25
  
- Databricks SQL Queries API
  - SDK: `databricks.sdk.service.sql` module
  - Used for: Creating, updating, and managing SQL queries
  - Implementation: `notebooks/functions.py` lines 50-61 (_create_sql_query method)
  - Authentication: Implicit via WorkspaceClient
  
- Databricks Alerts API
  - SDK: `databricks.sdk.service.sql` module (AlertOperator, AlertCondition, AlertConditionOperand, etc.)
  - Used for: Creating and managing alerts on query results
  - Implementation: `notebooks/functions.py` lines 63-94 (_create_sql_alert method)
  - Alert conditions support: >, >=, <, <=, ==, !=
  - Custom notifications: email subject and body templating with {{QUERY_RESULT_TABLE}}, {{QUERY_URL}}, {{ALERT_URL}}, {{ALERT_NAME}}, {{ALERT_STATUS}}, {{ALERT_CONDITION}}, {{ALERT_THRESHOLD}}

**System Tables Integration:**
- Source: `system.access.audit` - Databricks system table containing audit logs
- Queries defined in: `resources/queries_and_alerts.json`
- Primary use cases:
  - Login attempt monitoring
  - Admin user change tracking
  - Workspace configuration changes
  - Data access and download tracking
  - IP access list violations
  - Unity Catalog security events
  - Container isolation and security events

## Data Storage

**Databases:**
- Databricks Lakehouse (implicit)
  - System table: `system.access.audit` - audit logs
  - Connection: Through Databricks SQL warehouse
  - Client: Databricks SQL API via `databricks-sdk`
  - Warehouse selection: `terraform/variables.tf` allows optional `warehouse_id` parameter

**File Storage:**
- Local filesystem only - configuration files stored in git repo
  - `resources/queries_and_alerts.json` - JSON configuration file with all query and alert definitions

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Databricks Native Authentication
  - Implementation approach: Token-based via `DATABRICKS_HOST` and `DATABRICKS_TOKEN`
  - Location: `notebooks/functions.py` lines 21-25
  - Pattern: `WorkspaceClient()` auto-detects credentials from:
    - Environment variables: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`
    - Databricks CLI configuration file (~/.databricks/config)
    - Instance metadata (on Databricks compute)
  
- Alert Notifications:
  - Email subscriptions configured via Terraform
  - Recipients: Specified in `terraform/variables.tf` as `alert_emails` list
  - Implementation: `terraform/job.tf` lines 14-19 (dynamic subscriptions per alert)

## Monitoring & Observability

**Error Tracking:**
- None detected - errors logged via print() statements

**Logs:**
- Databricks notebook execution logs (implicit in notebook environment)
- Print statements for operation status: `notebooks/functions.py` lines 105, 113
- SQL audit events stored in `system.access.audit` table

**Audit Events:**
- 40+ security-focused SQL queries defined in `resources/queries_and_alerts.json`
- Categories:
  - Login security (failed attempts, repeated failures)
  - Admin changes (admin user assignments)
  - Workspace configuration changes
  - Data access patterns (downloads, UC requests)
  - IP access list violations
  - Token generation monitoring
  - Container/host security events

## CI/CD & Deployment

**Hosting:**
- Databricks Workspaces (SaaS platform)
- Deployed via either:
  1. Notebook execution: `notebooks/create_queries_and_alerts.py` run manually or scheduled
  2. Terraform: `terraform/` directory for IaC deployments

**CI Pipeline:**
- None detected in codebase
- Deployment is manual notebook execution or terraform apply

**Job Scheduling:**
- Databricks Jobs scheduled via Terraform
- Location: `terraform/job.tf`
- Schedule: Quartz cron expression "1 1 * * * ?" (daily at 01:01 UTC)
- Execution: SQL tasks with alert conditions and email subscriptions

## Environment Configuration

**Required env vars:**
- `DATABRICKS_HOST` - Databricks workspace URL (e.g., https://dbc-*.cloud.databricks.com)
- `DATABRICKS_TOKEN` - Personal access token for API authentication
- Implicitly passed to databricks-sdk WorkspaceClient

**Terraform Variables (terraform/variables.tf):**
- `warehouse_id` (optional, string, default "") - SQL warehouse ID for running queries
  - If empty: Creates new "Small" SQL endpoint with auto-stop of 5 minutes
  - If provided: Uses existing warehouse
- `alert_emails` (required, list of strings) - Email addresses to notify for alerts

**Secrets location:**
- Not stored in repo - credentials via environment or Databricks CLI config
- No .env files committed to git

## Webhooks & Callbacks

**Incoming:**
- Alert notifications: Email callbacks from Databricks when alert conditions are met
  - Customizable email subject and body templates defined in `resources/queries_and_alerts.json`
  - Example alert options: `custom_subject`, `custom_body` (lines 12-13, 37-38, etc.)

**Outgoing:**
- Email notifications only - no HTTP webhooks detected
- Alert subscription pattern: `terraform/job.tf` uses dynamic subscriptions with user_name

## Query & Alert Configuration

**Location:** `resources/queries_and_alerts.json`

**Configuration Structure:**
Each query/alert entry contains:
- `name` - Unique identifier
- `description` - What the query detects
- `query` - SQL query text (targets `system.access.audit`)
- `parent` - Workspace directory path for organization
- `alert` (optional) - Alert configuration if monitoring is enabled
  - `alert.name` - Alert display name
  - `alert.options` - Condition definition:
    - `column` - Which query result column to monitor
    - `op` - Operator: >, >=, <, <=, ==, !=
    - `value` - Threshold value
    - `custom_subject` - Email subject template
    - `custom_body` - Email body template with {{}} placeholders
  - `alert.rearm` - Seconds before alert can trigger again (re-arm time)
  - `alert.parent` - Workspace directory for alert organization

**Total Queries:** 40+ pre-configured security queries covering:
- Authentication/login security (5 queries)
- Admin/permission changes (3 queries)
- Workspace configuration (1 query)
- Data access and downloads (3 queries)
- IP access list monitoring (3 queries)
- Databricks support access (2 queries)
- Token and credential management (2 queries)
- Destructive activity detection (2 queries)
- Privilege escalation detection (2 queries)
- Secret access monitoring (2 queries)
- Cross-workspace access (1 query)
- Code quality monitoring (1 query)
- IP address tracking (2 queries)
- Unity Catalog security (6 queries)
- Delta Sharing security (3 queries)
- Usage analytics (2 queries)
- Container/host security events (4 queries)

---

*Integration audit: 2026-04-24*
