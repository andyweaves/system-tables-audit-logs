# Testing Patterns

**Analysis Date:** 2026-04-24

## Test Framework

**Runner:**
- No test framework detected
- No test configuration files found: no `pytest.ini`, `tox.ini`, or `setup.cfg`
- No test runner dependencies in `requirements.txt`

**Assertion Library:**
- Not applicable; no testing framework configured

**Run Commands:**
```bash
# No automated test commands configured
# Testing must be performed manually in Databricks notebook environment
```

## Test File Organization

**Location:**
- No test files found in repository
- No dedicated test directory structure
- No `.test.py` or `.spec.py` files detected
- Codebase relies on Databricks notebook environment for testing

**Naming:**
- Not applicable; no test files present

**Structure:**
- Not applicable; no test files present

## Test Structure

**Manual Testing Approach:**
- Testing performed directly in Databricks notebooks within the interactive environment
- `create_queries_and_alerts.py` notebook serves as integration test/execution environment
- Manual verification through notebook output and HTML table display
- No automated test suites

**Testing Pattern in Notebook:**
```python
# Tests performed via notebook execution:
sql_queries = read_json_file(json_file="../resources/queries_and_alerts.json")["queries_and_alerts"]
databricks_sql_helper = DatabricksSQLHelper()

for q in sql_queries:
    urls = databricks_sql_helper.create_sql_query_and_alert(query=q)
    q.update(urls)

# Results displayed via HTML output
pdf = (pd.json_normalize(sql_queries)[["query_url", "description", "alert_url"]]
       .rename(columns={"query_url": "query", "description": "query_description", "alert_url": "alert"}))
displayHTML(f"""<h1>The following SQL Queries and Alerts have been created:</h1>{build_table(pdf, 'blue_light')}""")
```

## Mocking

**Framework:**
- No mocking framework configured
- No mock libraries in dependencies

**Testing Approach:**
- Tests execute against live Databricks workspace API
- `DatabricksSQLHelper` class initializes real `WorkspaceClient()` from Databricks SDK
- No dependency injection or mock support evident

**What to Mock:**
- In any future testing framework, mock the `WorkspaceClient` to avoid creating actual objects in workspace
- Mock `workspace_client.queries.create()` to prevent test data pollution
- Mock `workspace_client.alerts.create()` for unit testing

**What NOT to Mock:**
- Business logic in `DatabricksSQLHelper` methods should be tested with real data flow
- SQL pattern matching and validation logic should test actual query construction

## Fixtures and Factories

**Test Data:**
- Configuration data loaded from `resources/queries_and_alerts.json`
- JSON structure serves as test fixture with defined queries and alert configurations
- Example fixture structure:
```json
{
  "queries_and_alerts": [
    {
      "name": "repeated_failed_login_attempts",
      "description": "...",
      "query": "SELECT ...",
      "parent": "system_tables/audit/admin/queries/",
      "alert": {
        "name": "...",
        "options": {
          "column": "total",
          "op": ">",
          "value": "1"
        },
        "rearm": "3600",
        "parent": "system_tables/audit/admin/alerts/"
      }
    }
  ]
}
```

**Location:**
- Test data located in `/resources/queries_and_alerts.json`
- Configuration loaded at runtime by `read_json_file()` utility
- 30+ pre-configured query and alert definitions available for testing

## Coverage

**Requirements:**
- No coverage requirements enforced
- No coverage reporting tools configured
- No coverage targets defined

**View Coverage:**
- Coverage measurement not available in current setup
- Would require pytest-cov or similar tool installation

## Test Types

**Unit Tests:**
- Not implemented
- Would benefit from unit testing of:
  - `read_json_file()` function with valid/invalid JSON
  - `DatabricksSQLHelper` initialization and configuration
  - Alert operator mapping logic in `_create_sql_alert()`
  - HTML table building in `build_table()`

**Integration Tests:**
- Functional integration testing performed via notebook execution
- `create_queries_and_alerts.py` serves as implicit integration test
- Tests creation of queries and alerts against live Databricks workspace
- Manual verification of created objects through workspace UI

**E2E Tests:**
- Not formally structured
- Implicit E2E: notebook runs against live Databricks workspace, creates real queries and alerts
- Verification through HTML table output showing created resource URLs
- Manual cleanup via setting `clean_up = True` flag

## Common Patterns

**Async Testing:**
- Not applicable
- No async/await patterns in codebase
- Databricks SDK methods are synchronous (blocking calls to workspace API)

**Error Testing:**
- Error handling tested through `_try_to_delete_dir()` which catches and logs `DatabricksError`
- Generic exception handling in `build_table()` function silently catches errors (lines 359-360, 370-371)
- No formalized error test cases

**Validation Testing Pattern:**
```python
# Implicit validation through conditional logic
if alert:  # Check if alert config exists
    a = self._create_sql_alert(alert=alert, qid=q.id)
    # Only creates alert if query creation succeeded

# Case statement validates alert operator values
match alert.get("options").get("op"):
    case ">":
        op = sql.AlertOperator.GREATER_THAN
    case ">=":
        op = sql.AlertOperator.GREATER_THAN_OR_EQUAL
    # ... other operators
```

## Recommended Testing Additions

**Unit Testing:**
- Add pytest configuration file
- Test `read_json_file()` with valid and invalid JSON
- Test `DatabricksSQLHelper` initialization
- Test alert operator mapping with all cases
- Mock Databricks API calls

**Integration Testing:**
- Create pytest fixtures for workspace client mocking
- Test query creation with various query configurations
- Test alert creation with various conditions and thresholds
- Test directory creation and cleanup operations

**Test Structure:**
```
tests/
├── unit/
│   ├── test_functions.py
│   └── test_databricks_helper.py
├── integration/
│   └── test_query_alert_creation.py
└── fixtures/
    └── test_queries_and_alerts.json
```

---

*Testing analysis: 2026-04-24*
