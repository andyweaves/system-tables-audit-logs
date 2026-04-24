# Codebase Concerns

**Analysis Date:** 2026-04-24

## Tech Debt

**Duplicate variable assignment in cleanup code:**
- Issue: Line 38 in `notebooks/create_queries_and_alerts.py` has a typo with duplicate assignment `directories =directories =`
- Files: `notebooks/create_queries_and_alerts.py:38`
- Impact: Code is syntactically valid but indicates copy-paste error. Could confuse maintainers and masks intent.
- Fix approach: Remove duplicate variable name: `directories = [x for pair in ...]`

**Duplicate operator mapping implementation:**
- Issue: Match/case statement in `notebooks/functions.py:66-78` duplicates the operator mapping logic that already exists in `terraform/sql.tf:4-11`
- Files: `notebooks/functions.py:66-78`, `terraform/sql.tf:4-11`
- Impact: Maintenance burden when adding new operators; inconsistency risk if one is updated without the other
- Fix approach: Extract operator mapping to shared `queries_and_alerts.json` config as a lookup reference, or create a centralized Python utilities module

**HTML table generation with brittle string manipulation:**
- Issue: The `build_table()` function in `notebooks/functions.py:178-395` uses extensive string replacement on HTML output
- Files: `notebooks/functions.py:315-331`
- Impact: Fragile approach prone to breaking if pandas DataFrame.to_html() output format changes; difficult to debug style issues
- Fix approach: Use a proper HTML templating library (Jinja2) or switch to pandas styling API

**Hard-coded exception handling with silent failures:**
- Issue: Multiple bare `except:` blocks catch all exceptions without logging or re-raising
- Files: `notebooks/functions.py:359-360, 371`
- Impact: Bugs silently fail, making debugging difficult; invalid input silently produces no output in table formatting
- Fix approach: Replace with specific exception types and add logging; use try-except-else patterns

**Bare except with pass statements:**
- Issue: Lines 359 and 371 in `notebooks/functions.py` have bare except blocks with `pass` statements
- Files: `notebooks/functions.py:359, 371`
- Impact: Masks underlying errors during table formatting; when conditional logic fails, no indication is given to user
- Fix approach: Log exceptions at DEBUG level and add informative output when formatting fails

## Missing Error Handling

**No validation of alert configuration:**
- Issue: Alert operator (`op`) is extracted from JSON and mapped without validation in `notebooks/functions.py:66-78`
- Files: `notebooks/functions.py:66-78`
- Impact: If invalid operator is in `queries_and_alerts.json`, no error is raised; alert creation fails silently
- Recommendation: Add explicit validation that `alert.get("options").get("op")` exists and is in known set before match statement

**Uninitialized match variable:**
- Issue: Variable `op` is assigned in match/case statement `notebooks/functions.py:66-78` but has no default case
- Files: `notebooks/functions.py:66-78`
- Impact: If operator string from JSON is not in any case, `op` will be undefined when used on line 83, causing NameError at alert creation time
- Recommendation: Add `case _: raise ValueError(f"Unknown operator: {alert.get('options').get('op')}")`

**No validation of required JSON fields:**
- Issue: Code assumes all required fields exist in `queries_and_alerts.json` without validation
- Files: `notebooks/functions.py:50-61, 63-94`, `notebooks/create_queries_and_alerts.py:11-18`
- Impact: KeyError if expected fields missing; JSON structure changes silently break the entire run
- Recommendation: Validate JSON schema at load time in `read_json_file()` function

## Known Bugs

**Unused variable `sources`:**
- Symptoms: Instance variable `self.sources` is assigned but never used
- Files: `notebooks/functions.py:23, 40-42`
- Trigger: Initialize DatabricksSQLHelper instance
- Impact: Indicates incomplete implementation or dead code; wastes API call at initialization

**Optional alert without handling null path:**
- Symptoms: When processing queries, code calls `.get("alert").get("parent")` on optional alert
- Files: `notebooks/create_queries_and_alerts.py:38`
- Trigger: When processing list of queries where some have no alert
- Impact: On queries without alerts, this returns AttributeError when calling .get("parent") on None
- Workaround: Code uses `sql.get("alert") is not None` check beforehand, but structure is fragile

## Security Considerations

**SDK initialization with default credentials:**
- Risk: `WorkspaceClient()` uses default Databricks credential chain without explicit validation
- Files: `notebooks/functions.py:21`
- Current mitigation: Relies on environment authentication configured outside the notebook
- Recommendations: 
  - Add validation that client is authenticated before proceeding
  - Log workspace URL and user being used for audit trail
  - Consider adding explicit authentication error handling

**SQL injection in dynamically constructed queries:**
- Risk: Query text is loaded from JSON and passed directly to Databricks API without validation
- Files: `resources/queries_and_alerts.json`, `notebooks/functions.py:58`
- Current mitigation: JSON is static configuration file, not user input; Databricks SDK uses parameterized queries
- Recommendations:
  - Document that query text in JSON should be treated as trusted configuration
  - Consider schema validation for SQL queries (basic structure check)

**No access control on cleanup function:**
- Risk: `clean_up` flag in `notebooks/create_queries_and_alerts.py:35` enables deletion of all queries/alerts without confirmation
- Files: `notebooks/create_queries_and_alerts.py:35-39`
- Current mitigation: Flag defaults to False; user must explicitly set it
- Recommendations:
  - Require explicit confirmation prompt before deletion
  - Log all deleted resources with timestamps
  - Consider restricting cleanup to notebook admins only

**Sensitive data in alert emails:**
- Risk: Custom alert body includes full `{{QUERY_RESULT_TABLE}}` which may contain sensitive audit information
- Files: `resources/queries_and_alerts.json` (all alerts with custom_body)
- Current mitigation: Alerts are configured by Databricks admins
- Recommendations:
  - Document email recipient access control requirements
  - Consider redacting sensitive columns in alert output templates

## Performance Bottlenecks

**Sequential API calls for each query/alert creation:**
- Problem: Loop processes queries one at a time, making blocking API calls
- Files: `notebooks/create_queries_and_alerts.py:15-18`
- Cause: Notebook script is synchronous; each query/alert creation waits for previous completion
- Scaling limit: Creating 50+ queries/alerts will take several minutes
- Improvement path: Implement async/concurrent API calls using ThreadPoolExecutor; batch operations where possible

**Large table HTML generation with string replacement:**
- Problem: HTML table formatting uses nested loops and string replacement on entire HTML output
- Files: `notebooks/functions.py:210-331`
- Cause: Iterating through DataFrame rows and applying regex-like string replacements for each row
- Scaling limit: Tables with >1000 rows will become slow; memory usage grows quadratically
- Improvement path: Generate HTML directly using Jinja2 templates or pandas styling instead of post-processing

**Full query reload in Terraform for every apply:**
- Problem: Terraform reads entire JSON file and regenerates all queries/alerts even if only one changed
- Files: `terraform/main.tf:16`, `terraform/sql.tf:28-38, 40-57`
- Cause: Terraform uses for_each on decoded JSON; no change detection at field level
- Scaling limit: With 50+ queries, Terraform plan becomes slow
- Improvement path: Use Terraform modules to generate resources dynamically; consider splitting into smaller configuration files

## Fragile Areas

**HTML string manipulation in build_table():**
- Files: `notebooks/functions.py:178-395`
- Why fragile: Complex regex-like string replacement on HTML; assumes specific pandas to_html() output format; relies on counting `<td>` and `<th>` tags to track column position
- Safe modification: Test thoroughly with various DataFrame shapes before modifying; consider replacing with Jinja2 templates instead
- Test coverage: No unit tests for table formatting; edge cases unknown (empty columns, special characters, unicode)

**JSON configuration as source of truth:**
- Files: `resources/queries_and_alerts.json` (663 lines)
- Why fragile: Configuration is large and monolithic; manual edits require careful JSON syntax; no schema validation
- Safe modification: Use JSON schema validator (jsonschema package) to validate before processing; split into smaller files by category
- Test coverage: No validation; typos in JSON break entire notebook run

**Alert operator matching:**
- Files: `notebooks/functions.py:66-78`
- Why fragile: Match/case statement has no default case; silently creates undefined behavior if operator missing
- Safe modification: Add comprehensive case with error handling; add logging for which operator was selected
- Test coverage: No unit tests for different operator types

**Workspace directory creation with hardcoded paths:**
- Files: `notebooks/functions.py:46`, `terraform/main.tf:25`
- Why fragile: Uses `WorkspaceClient.current_user.me()` which requires authenticated session; assumes user has directory creation permissions
- Safe modification: Add permission checks before creation; log actual path created
- Test coverage: No error handling for permission denied scenarios

## Test Coverage Gaps

**No unit tests:**
- What's not tested: DatabricksSQLHelper class methods, operator mapping, error scenarios
- Files: `notebooks/functions.py`, `notebooks/create_queries_and_alerts.py`
- Risk: Changes to SDK API version could break functionality silently; refactoring could introduce regressions
- Priority: High - Core API integration logic should have unit tests

**No integration tests:**
- What's not tested: Actual query/alert creation against Databricks workspace; JSON loading and validation
- Files: All notebook code
- Risk: SQL syntax errors in queries_and_alerts.json not caught until runtime; Databricks API changes not caught
- Priority: High - Should test against development workspace before production use

**No table formatting unit tests:**
- What's not tested: HTML generation with various DataFrame shapes; edge cases with special characters
- Files: `notebooks/functions.py:178-395` (build_table function)
- Risk: HTML output may be malformed for certain data patterns; styling logic may fail silently
- Priority: Medium - Affects output quality but not core functionality

**No Terraform validation:**
- What's not tested: Whether Terraform configuration produces valid Databricks resources
- Files: `terraform/`
- Risk: Plan may look valid but apply fails; syntax errors not caught until plan/apply
- Recommendation: Add `terraform validate`, `terraform plan` to CI/CD; test with sample data

## Dependencies at Risk

**Unbounded databricks-sdk version:**
- Risk: `requirements.txt` specifies only `databricks-sdk` with no version pin
- Impact: Major version changes could introduce breaking changes; inconsistent environments across developers
- Migration plan: Pin to specific major version `databricks-sdk>=1.20,<2.0`; test with new versions before upgrade

**Python 3.10+ requirement for match/case:**
- Risk: Match/case syntax in `notebooks/functions.py:66-78` requires Python 3.10+
- Impact: Cannot run on Python 3.9 or earlier; some Databricks runtime versions may not support
- Migration plan: Check Databricks runtime version support; consider backporting to if-elif for compatibility

## Missing Critical Features

**No dry-run mode:**
- Problem: Cannot preview what will be created without actually creating resources
- Blocks: Validation of configuration changes; testing in safe manner
- Recommendation: Add `--dry-run` flag to notebook that logs what would be created without calling APIs

**No incremental updates:**
- Problem: Deleting and recreating all queries/alerts is the only update mechanism
- Blocks: Non-destructive updates; preserving alert history; custom query modifications
- Recommendation: Implement resource comparison to only create/update changed items; preserve query IDs

**No alert notification delivery testing:**
- Problem: No way to verify alert emails/webhooks are configured correctly
- Blocks: Confidence that alerts will actually fire; debugging notification issues
- Recommendation: Add test alert trigger that sends sample notification with known data

**No query result sampling in alerts:**
- Problem: Alert body includes full query results which may be too large or sensitive
- Blocks: Safe alerting on large result sets; restricting sensitive data in emails
- Recommendation: Add configuration for result row limit and column selection in alert templates

## Documentation Gaps

**No inline code comments:**
- Files: `notebooks/functions.py`, `notebooks/create_queries_and_alerts.py`
- Impact: Complex logic like HTML string manipulation is undocumented; entry point requirements unclear

**No error handling documentation:**
- What's missing: How to troubleshoot common failures; what to do if queries fail to create
- Impact: Users have no guidance for debugging when something goes wrong

**No prerequisites documentation:**
- What's missing: Required Databricks permissions, SDK version requirements, Python version requirements
- Impact: Notebook may fail silently if run in incompatible environment

---

*Concerns audit: 2026-04-24*
