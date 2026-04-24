# Technology Stack

**Analysis Date:** 2026-04-24

## Languages

**Primary:**
- Python 3.x - Notebook-based implementation for query and alert creation
- SQL - Databricks SQL for audit log queries (defined in `resources/queries_and_alerts.json`)
- HCL (Terraform) - Infrastructure as code for deploying queries, alerts, and jobs

**Secondary:**
- JSON - Configuration and data serialization (`resources/queries_and_alerts.json`)

## Runtime

**Environment:**
- Databricks Notebooks (Python Runtime)
- Databricks SQL Warehouse - for executing audit queries and running alerts
- Terraform Runtime - for IaC deployments

**Package Manager:**
- pip - Python package management
- Lockfile: `requirements.txt` (single dependency, no lock file present)

## Frameworks

**Core:**
- databricks-sdk [version unspecified in requirements.txt] - Databricks Python API client
  - Used for creating SQL queries and alerts programmatically
  - Location: `notebooks/functions.py`

**Data Processing:**
- pandas (imported but not in requirements.txt, likely implicit dependency) - Data manipulation
  - Used for DataFrame formatting and HTML table generation
  - Location: `notebooks/create_queries_and_alerts.py`

**Infrastructure:**
- Terraform >= 1.59.0, < 2.0.0 - Databricks provider for IaC
  - Declared in `terraform/main.tf`
  - Alternative to notebook-based approach

## Key Dependencies

**Critical:**
- databricks-sdk - Enables programmatic creation of SQL queries and alerts in Databricks
  - Required env var: `DATABRICKS_HOST` and `DATABRICKS_TOKEN` (default auth via WorkspaceClient)
  - Provides: WorkspaceClient, alerts API, SQL query API

**Infrastructure:**
- Terraform Databricks Provider >= 1.59.0 - IaC support for queries, alerts, SQL warehouses, jobs
  - Location: `terraform/`
  - Manages: SQL endpoints, queries, alerts, directories, jobs

## Configuration

**Environment:**
- Databricks workspace authentication via:
  - `DATABRICKS_HOST` - workspace instance URL
  - `DATABRICKS_TOKEN` - personal access token
  - Default: Uses WorkspaceClient() which auto-detects from Databricks CLI config or environment
- Source: `notebooks/functions.py` lines 21-25

**Build:**
- requirements.txt - Single dependency definition
- terraform/variables.tf - Terraform variables:
  - `warehouse_id` (optional) - SQL warehouse to use, creates new "System Tables" endpoint if not provided
  - `alert_emails` (required) - List of email addresses to notify when alerts fire

## Platform Requirements

**Development:**
- Python 3.x runtime (Databricks notebook environment)
- Databricks workspace with SQL capability
- Terraform >= 1.5 (for provider support)

**Production:**
- Deployment target: Databricks Account (workspace-level deployments)
- Databricks SQL Warehouse for executing queries and alerts
- Databricks Jobs for scheduled alert execution
- Required permissions: ability to create queries, alerts, directories, jobs, SQL endpoints

## Notebooks Entry Points

**Primary:**
- `notebooks/create_queries_and_alerts.py` - Main entry point for creating queries and alerts from configuration
  - Installs dependencies from `requirements.txt`
  - Calls `DatabricksSQLHelper` to create queries and alerts
  - Outputs HTML table with links to created resources

**Utilities:**
- `notebooks/functions.py` - Helper functions and classes
  - `read_json_file()` - JSON configuration loader
  - `DatabricksSQLHelper` class - Core API client for query and alert operations
  - `build_table()` - HTML table generation from DataFrames

## Terraform Entry Points

**Primary:**
- `terraform/main.tf` - Provider configuration and directory structure creation
- `terraform/sql.tf` - SQL queries and alerts resource definitions
- `terraform/job.tf` - Databricks job for scheduled alert execution

---

*Stack analysis: 2026-04-24*
