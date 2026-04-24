# Coding Conventions

**Analysis Date:** 2026-04-24

## Naming Patterns

**Files:**
- Python files use snake_case: `functions.py`, `create_queries_and_alerts.py`
- Databricks notebooks use `.py` extension with descriptive names indicating purpose
- Configuration files use snake_case with clear intent: `queries_and_alerts.json`

**Functions:**
- Snake_case naming convention used for all function definitions
- Example: `read_json_file()`, `_get_context()`, `_create_sql_query()`
- Private/internal functions prefixed with single underscore: `_get_sources()`, `_get_or_create_parent()`
- Public methods do not use underscore prefix

**Variables:**
- Snake_case for variable names: `workspace_client`, `browser_host_name`, `org_id`
- Dictionary/object variables use descriptive snake_case: `dict_colors`, `sql_queries`
- Loop counters use single letters: `a`, `w`, `d`
- Configuration dictionary keys use snake_case: `display_name`, `query_text`, `parent_path`

**Types:**
- Class names use PascalCase: `DatabricksSQLHelper`
- Type hints used in function signatures, e.g., `def read_json_file(json_file: str) -> dict:`
- Return type annotations present for important functions

## Code Style

**Formatting:**
- No explicit formatter configured (no `.prettierrc` or equivalent found)
- Indentation appears consistent at 2 spaces in notebook cells, variable indentation in class methods
- Line length varies; some lines exceed typical 80-character limits (e.g., lines 212-230 in `functions.py`)
- No black, autopep8, or yapf configuration detected

**Linting:**
- No linting configuration found (no `.pylintrc`, `.flake8`, or `pyproject.toml`)
- No enforced linting rules detected in repository
- Code style is not strictly enforced

## Import Organization

**Order:**
1. Standard library imports at top: `json`, `io`
2. Third-party SDK imports: `databricks.sdk`, `IPython.display`
3. Service-specific imports: `databricks.sdk.core`, `databricks.sdk.service`

**Path Organization:**
- Databricks Notebook `%run ./functions` used in `create_queries_and_alerts.py` to import from sibling notebook
- Relative imports used for notebook dependencies
- Configuration file loaded via relative path: `../resources/queries_and_alerts.json`

**Import Examples:**
```python
# Standard library
import json
import io

# Third-party with Databricks SDK
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError
from databricks.sdk.service import sql
from IPython.display import display, HTML
```

## Error Handling

**Patterns:**
- Try/except blocks used for expected failures: `except DatabricksError as e:` in `_try_to_delete_dir()`
- Generic exception handling: `except:` used in `build_table()` function (lines 359-360, 370-371) for silent failure modes
- Error logging via print statements: `print(e)` when DatabricksError caught
- No custom exception classes defined; relies on Databricks SDK exceptions

**Example Error Handling:**
```python
def _try_to_delete_dir(self, directory):
    print(f"Attempting to delete directory {directory}")
    try:
        self.workspace_client.workspace.delete(directory, recursive=True)
    except DatabricksError as e:
        print(e)
```

## Logging

**Framework:** Console-based using Python `print()` statements

**Patterns:**
- Status messages logged via `print()`: `print(f"Successfully created query '{q.display_name}' with id {q.id}")`
- No structured logging framework (no logging module imports detected)
- Logging used to communicate operation results in notebook context: creation success, deletion attempts
- Progress tracking in loops via print statements

**Logging Examples:**
```python
print(f"Successfully created query '{q.display_name}' with id {q.id}")
print(f"Successfully created alert '{a.display_name}' with id {a.id}")
print(f"Attempting to delete directory {directory}")
```

## Comments

**When to Comment:**
- License headers included for modified third-party code (MIT License in `build_table()`)
- Attribution comments provided: `# Modified version of https://github.com/sbi-rviot/ph_table/tree/master`
- Inline comments sparse; code structure and naming provide clarity
- No docstrings observed for functions

**JSDoc/TSDoc:**
- Not applicable to Python codebase
- Type hints provide some documentation: `def read_json_file(json_file: str) -> dict:`
- No pydoc-style documentation strings found

## Function Design

**Size:** 
- Functions range from very small (1-3 lines like `get_workspace_client()`) to large (200+ lines like `build_table()`)
- `build_table()` contains complex HTML manipulation logic spanning 220 lines, indicating less concern for function size limits
- Helper methods organized to separate concerns: `_create_sql_query()`, `_create_sql_alert()`, `_try_to_delete_dir()`

**Parameters:**
- Functions accept explicit parameters with type hints in modern style
- Default parameters used in `build_table()` for optional styling: `font_size='medium'`, `index=False`
- Varied parameter count; `build_table()` has 15 parameters, indicating some functions handle complex configurations
- Dictionary/object parameters used for grouped configuration: `alert`, `query` parameters in methods

**Return Values:**
- Explicit return types: `-> dict`, `-> str`, `-> WorkspaceClient`, `-> None`
- Some functions return dictionary updates: `self.urls` in `create_sql_query_and_alert()`
- Empty string returned for certain conditions: `return ''` in `build_table()`
- HTML strings built and returned from formatting functions

**Example Function:**
```python
def create_sql_query_and_alert(self, query) -> None:
    self.urls.clear()
    q = self._create_sql_query(query=query)
    print(f"Successfully created query '{q.display_name}' with id {q.id}")
    self.urls.update({"query_url": f"<a href='https://{self.base_url}/sql/editor/{q.id}?o={self.org_id}'>{q.display_name}</a>"})
    # ... conditional alert creation
    return self.urls
```

## Module Design

**Exports:**
- Databricks notebooks use `# COMMAND ----------` to separate logical cells for execution
- Functions and classes explicitly defined and available for import
- `read_json_file()` function available as utility
- `DatabricksSQLHelper` class is main export from `functions` notebook
- `build_table()` utility function exported for use in display logic

**Barrel Files:**
- Not applicable; Databricks notebooks don't use barrel pattern
- Notebook `%run ./functions` syntax imports all definitions from referenced notebook
- Configuration loaded from JSON file at runtime

**Databricks Notebook Structure:**
```python
# COMMAND ----------  # Cell separator
# MAGIC %pip install ...  # Magic command
# MAGIC %run ./functions  # Import another notebook
```

---

*Convention analysis: 2026-04-24*
