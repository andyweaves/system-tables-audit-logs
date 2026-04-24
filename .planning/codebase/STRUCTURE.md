# Codebase Structure

**Analysis Date:** 2026-04-24

## Directory Layout

```
system-tables-audit-logs/
├── notebooks/               # Databricks notebook workflows
│   ├── create_queries_and_alerts.py      # Main entry point: reads config and creates queries/alerts
│   ├── functions.py                       # Helper classes and utilities (DatabricksSQLHelper, HTML rendering)
│   └── geolocation_function_and_queries.sql # Optional IP geolocation enrichment functions
├── terraform/              # Infrastructure-as-code for automated deployment
│   ├── main.tf             # Databricks provider config and directory structure
│   ├── sql.tf              # SQL query, alert, and warehouse resources
│   ├── job.tf              # Scheduled job for running alerts
│   ├── variables.tf        # Terraform variables (warehouse_id, alert_emails)
│   └── README.md           # Terraform setup instructions
├── resources/              # Configuration and data files
│   └── queries_and_alerts.json  # Single source of truth: all query/alert definitions
├── .planning/              # GSD planning documents
│   └── codebase/           # Architecture and structure analysis
├── requirements.txt        # Python dependencies (databricks-sdk)
├── README.md              # Project documentation
└── LICENSE                # License file
```

## Directory Purposes

**notebooks/:**
- Purpose: Databricks notebook-based workflows for query and alert creation
- Contains: Python notebooks using Databricks SDK to interact with workspace
- Key files: `create_queries_and_alerts.py` (main), `functions.py` (utilities)
- Execution context: Databricks notebook environment with automatic auth

**terraform/:**
- Purpose: Infrastructure-as-code for declarative resource provisioning
- Contains: HCL (HashiCorp Configuration Language) files for Databricks resources
- Key files: `main.tf`, `sql.tf`, `job.tf`, `variables.tf`
- Execution context: Local CLI or CI/CD pipeline with Databricks provider auth

**resources/:**
- Purpose: Configuration data files used by both deployment methods
- Contains: JSON schema defining queries, alerts, and their properties
- Key files: `queries_and_alerts.json` (40+ audit security queries)
- Single source of truth for all query and alert definitions

**.planning/codebase/:**
- Purpose: GSD codebase analysis documents
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, STACK.md

## Key File Locations

**Entry Points:**
- `notebooks/create_queries_and_alerts.py`: Notebook-based entry point for interactive creation
- `terraform/main.tf`: Terraform entry point for infrastructure definition
- `notebooks/geolocation_function_and_queries.sql`: Optional enhancement setup

**Configuration:**
- `resources/queries_and_alerts.json`: Central configuration - defines all 40+ security queries and alerts
- `terraform/variables.tf`: Terraform variables for warehouse_id and alert_emails
- `requirements.txt`: Python dependencies (databricks-sdk)

**Core Logic:**
- `notebooks/functions.py`: DatabricksSQLHelper service class (lines 19-133)
- `notebooks/functions.py`: HTML table builder for output rendering (lines 136-200+)
- `terraform/sql.tf`: Resource definitions for queries, alerts, warehouse (lines 1-64)
- `terraform/job.tf`: Scheduled job configuration (lines 1-35)

**Documentation:**
- `README.md`: Main project overview, setup instructions, query catalog
- `terraform/README.md`: Terraform-specific setup and deployment guide

## Naming Conventions

**Files:**
- Python files: snake_case (e.g., `create_queries_and_alerts.py`, `functions.py`)
- HCL files: snake_case (e.g., `main.tf`, `variables.tf`, `sql.tf`)
- JSON config: snake_case with underscores for multi-word names
- Markdown docs: UPPERCASE.md (README.md, ARCHITECTURE.md, STRUCTURE.md)

**Directories:**
- lowercase_with_underscores: `notebooks/`, `terraform/`, `resources/`, `.planning/`

**Python Classes:**
- PascalCase: `DatabricksSQLHelper`

**Python Functions/Methods:**
- snake_case: `read_json_file()`, `_create_sql_query()`, `build_table()`
- Private methods prefixed with underscore: `_get_sources()`, `_try_to_delete_dir()`

**Terraform Resources:**
- Descriptive names matching purpose: `databricks_directory`, `databricks_query`, `databricks_alert`
- For-each loops with meaningful keys: `for_each = local.queries`, `for_each = local.alerts`

**JSON Configuration:**
- Query/alert names: snake_case_descriptive (e.g., `repeated_failed_login_attempts`, `changes_to_admin_users`)
- Object keys: snake_case (e.g., `parent`, `alert`, `custom_subject`, `query_text`)

## Where to Add New Code

**New Security Query/Alert:**
1. Add new object to `resources/queries_and_alerts.json` following the schema:
   ```json
   {
     "name": "descriptive_name",
     "description": "What this detects",
     "query": "SELECT ... FROM system.access.audit WHERE ...",
     "parent": "system_tables/audit/admin/queries/",
     "alert": { ... }  // optional
   }
   ```
2. Schema: required fields are `name`, `description`, `query`, `parent`
3. Alert is optional but follows pattern: options with column, operator, threshold, message templates
4. Both notebook and Terraform automatically read and deploy from this config file

**New Utility Function:**
- Location: `notebooks/functions.py`
- Pattern: Add to appropriate class (`DatabricksSQLHelper` for SDK operations) or as module-level function
- Dependencies: Must be importable via `# MAGIC %run ./functions` in notebooks

**New Terraform Module/Behavior:**
- Location: Create new `.tf` file in `terraform/` directory
- Pattern: Reference local variables computed in `main.tf` (e.g., `local.queries`, `local.data_map`)
- Dependencies: Declare in provider and data sources, compute in main.tf locals

**Geolocation Enhancement:**
- Location: Add queries to `notebooks/geolocation_function_and_queries.sql`
- Prerequisites: GeoLite2 data must be loaded into workspace tables first
- Pattern: Use `inet_aton()` UDF and range joins to enrich audit logs with location data

## Special Directories

**.planning/codebase/:**
- Purpose: GSD codebase mapping and analysis documents
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, STACK.md, CONCERNS.md
- Generated: Yes - by GSD tools
- Committed: Yes - part of repo for reference

**.git/:**
- Purpose: Version control
- Contains: Git history and configuration
- Generated: Yes
- Committed: No (directory itself not committed)

**terraform/ (local state):**
- Purpose: Terraform working directory
- Contains: .terraform/ (after init), terraform.tfvars (user-specific, not committed)
- Generated: Yes - during `terraform init` and `terraform apply`
- Committed: terraform.tfvars should be .gitignored for secrets safety

## Deployment Patterns

**Pattern 1: Notebook-Based (Interactive)**
1. Clone repo into Databricks workspace via Repos feature
2. Navigate to `notebooks/create_queries_and_alerts.py`
3. Execute notebook manually
4. Queries and alerts created in workspace under user's home directory
5. Optional: Set `clean_up = True` to remove previously created assets

**Pattern 2: Terraform-Based (Infrastructure-as-Code)**
1. Clone repo locally
2. Create `terraform/terraform.tfvars` with alert_emails and optional warehouse_id
3. Run `terraform init`
4. Run `terraform plan` to review changes
5. Run `terraform apply` to create all resources
6. Scheduled job automatically runs alert checks every hour

---

*Structure analysis: 2026-04-24*
