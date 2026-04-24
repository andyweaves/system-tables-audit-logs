# Architecture

**Analysis Date:** 2026-04-24

## Pattern Overview

**Overall:** Configuration-Driven Query & Alert Factory

**Key Characteristics:**
- Single source of truth: JSON configuration file defines all queries and alerts
- Multi-layer deployment options: notebook-based (Databricks SDK) or infrastructure-as-code (Terraform)
- Data retrieval from Databricks System Tables (`system.access.audit`)
- Automated creation and management of SQL queries and alerts
- Notification-driven alerting with customizable conditions and email recipients

## Layers

**Configuration Layer:**
- Purpose: Store all query and alert definitions as structured data
- Location: `resources/queries_and_alerts.json`
- Contains: Query names, descriptions, SQL text, alert thresholds, notification bodies
- Depends on: Nothing
- Used by: Both notebook and Terraform workflows

**Orchestration Layer (Notebook-based):**
- Purpose: Programmatically create SQL queries and alerts via Databricks SDK
- Location: `notebooks/create_queries_and_alerts.py`
- Contains: Main workflow that reads config and triggers creation
- Depends on: Databricks SDK, Helper utilities
- Used by: Direct notebook execution in Databricks workspace

**Orchestration Layer (Infrastructure-as-Code):**
- Purpose: Declaratively create SQL queries, alerts, and jobs via Terraform
- Location: `terraform/` (main.tf, sql.tf, job.tf)
- Contains: Terraform resources for directories, queries, alerts, SQL warehouse, and scheduled jobs
- Depends on: Databricks Terraform provider, configuration file
- Used by: `terraform plan` and `terraform apply`

**Service Layer:**
- Purpose: Provide Databricks API abstractions and helper functions
- Location: `notebooks/functions.py`
- Contains: `DatabricksSQLHelper` class with SDK wrapper methods
- Depends on: Databricks SDK, workspace context
- Used by: `create_queries_and_alerts.py` notebook

**Utility Layer:**
- Purpose: Support functions for data handling and HTML rendering
- Location: `notebooks/functions.py` (utility functions)
- Contains: JSON file reading, HTML table building with styling
- Depends on: Python standard library, pandas, Databricks utilities
- Used by: Orchestration and service layers

**Geolocation Enhancement Layer:**
- Purpose: Optional IP geolocation enrichment for audit analysis
- Location: `notebooks/geolocation_function_and_queries.sql`
- Contains: SQL UDF for IP-to-integer conversion, geolocation join queries
- Depends on: GeoLite2 CSV data loaded as tables, Databricks SQL
- Used by: Optional geolocation-based queries

## Data Flow

**Notebook Execution Flow:**

1. Notebook environment setup and dependency installation (`%pip install`)
2. Load helper functions from `notebooks/functions.py`
3. Read configuration from `resources/queries_and_alerts.json`
4. Initialize `DatabricksSQLHelper` (connects to workspace, discovers SQL warehouses)
5. Iterate through each query definition
6. For each query:
   - Create SQL query via SDK using `_create_sql_query()` method
   - If alert defined, create alert via SDK using `_create_sql_alert()` method
   - Capture URLs and metadata
7. Generate and display HTML output showing created queries and alerts
8. Optional: cleanup existing queries and alerts if `clean_up = True`

**Terraform Execution Flow:**

1. Load and parse `queries_and_alerts.json`
2. Compute derived values: directories, query names, alert names, data mappings
3. Create workspace directories for query/alert organization
4. Create/use SQL warehouse (create new or reference existing by ID)
5. Create SQL queries mapped to warehouse
6. Create SQL alerts mapped to queries
7. Create scheduled job that runs alert checks on 1-hour cron

**Data Source:**

- Queries execute against `system.access.audit` table in Databricks
- Geolocation queries supplement with GeoLite2 data (optional)
- Results used for alerting and compliance reporting

**State Management:**

- Query/Alert definitions: stored in JSON configuration file
- Query/Alert metadata: stored in Databricks SQL service
- Jobs and alerts: managed by Databricks scheduler
- No local application state; all state in Databricks workspace

## Key Abstractions

**DatabricksSQLHelper:**
- Purpose: Encapsulate Databricks SDK interaction patterns
- Examples: `notebooks/functions.py` (lines 19-133)
- Pattern: Class-based wrapper providing context detection, resource creation, deletion

**Query Definition Schema:**
- Purpose: Standardize how queries and alerts are described
- Examples: `resources/queries_and_alerts.json` (each object in `queries_and_alerts` array)
- Pattern: Dictionary with required fields (name, description, query, parent) and optional alert sub-object

**Alert Definition Schema:**
- Purpose: Specify alert conditions and notification behavior
- Examples: `resources/queries_and_alerts.json` (alert objects within query definitions)
- Pattern: Nested object with options (column, operator, threshold, custom message templates)

## Entry Points

**Notebook Entry Point:**
- Location: `notebooks/create_queries_and_alerts.py`
- Triggers: Manual notebook execution in Databricks workspace
- Responsibilities: Read config, instantiate helper, iterate and create resources, render output

**Terraform Entry Points:**
- Location: `terraform/main.tf`, `terraform/sql.tf`, `terraform/job.tf`
- Triggers: `terraform apply` command
- Responsibilities: Provision directories, queries, alerts, warehouse, job based on config

**Geolocation Setup:**
- Location: `notebooks/geolocation_function_and_queries.sql`
- Triggers: Manual execution after GeoLite2 data preparation
- Responsibilities: Create UDF and example queries for geolocation-enriched analysis

## Error Handling

**Strategy:** Exception capture with logging and user feedback

**Patterns:**
- SDK exceptions caught as `DatabricksError` in `_try_to_delete_dir()` method (`notebooks/functions.py`, line 124)
- Workspace context accessed via `_get_context()` - fails if not in notebook environment
- JSON parsing assumes valid JSON; no schema validation on configuration file
- Optional fields in configuration use `.get()` with fallback for missing alerts

## Cross-Cutting Concerns

**Logging:** 
- Notebook: print statements for operation success/failure (`notebooks/functions.py`, lines 105, 113)
- Terraform: standard Terraform output with resource creation/modification summaries

**Validation:**
- Configuration structure assumed valid; no runtime validation
- Alert operator mapping must match defined operators (`notebooks/functions.py` lines 66-78)
- Query text assumed valid SQL; executed as-is

**Authentication:**
- Notebook: automatic via `WorkspaceClient()` using workspace default credentials
- Terraform: via provider configuration or environment variables (details in terraform/README.md)

---

*Architecture analysis: 2026-04-24*
