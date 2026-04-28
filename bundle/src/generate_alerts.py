"""Preinit generator: reads resources/queries_and_alerts.json and writes
bundle/generated/alerts.yml with one Alerts v2 resource per alertable entry.

This script is invoked by `experimental.scripts.preinit` in bundle/databricks.yml
before `databricks bundle validate` or `databricks bundle deploy`.

Design notes:
- Operator map sourced from terraform/sql.tf (NOT notebooks/functions.py, which
  has a `<=` -> LESS_THAN bug). See GEN-05 in REQUIREMENTS.md.
- Every alert emits a notification.subscriptions block. Omitting this is the #1
  pitfall: alerts deploy and fire but never send email.
- Variable references (${var.*}) are emitted as literal strings. The DAB CLI
  resolves them at deploy time; this generator never sees real values.
"""

import json
import sys
from pathlib import Path

import yaml

# Paths relative to repo root (the bundle root — see bundle/databricks.yml).
REPO_ROOT = Path(__file__).resolve().parents[2]
JSON_CONFIG = REPO_ROOT / "resources" / "queries_and_alerts.json"
OUTPUT_DIR = REPO_ROOT / "bundle" / "generated"
OUTPUT_FILE = OUTPUT_DIR / "alerts.yml"

# Sourced from terraform/sql.tf lines 4-11 (verified correct against CLI 0.288.0
# bundle schema). Do NOT copy from notebooks/functions.py:74 — it maps `<=` to
# LESS_THAN instead of LESS_THAN_OR_EQUAL.
OPS_MAPPING = {
    ">":  "GREATER_THAN",
    ">=": "GREATER_THAN_OR_EQUAL",
    "<":  "LESS_THAN",
    "<=": "LESS_THAN_OR_EQUAL",   # regression guard: notebooks/functions.py:74 maps this to LESS_THAN (bug)
    "==": "EQUAL",
    "!=": "NOT_EQUAL",
}

# Dotted paths that every alertable entry must supply. Used by validate_entry().
REQUIRED_ALERT_FIELDS = [
    "name",
    "query",
    "alert.name",
    "alert.rearm",
    "alert.options.op",
    "alert.options.column",
    "alert.options.value",
]


def _threshold_value(raw_value):
    """Pack a raw JSON threshold value into the Alerts v2 typed wrapper.

    Alerts v2 rejects `string_value` thresholds when the source column is
    numeric (e.g. COUNT aggregates return BIGINT) with
    "Incompatible type in alert evaluation" / INVALID_PARAMETER_VALUE.
    All thresholds in queries_and_alerts.json are numeric counts/sums stored
    as JSON strings; cast to double when parseable, otherwise fall back to
    string.
    """
    if isinstance(raw_value, bool):
        return {"bool_value": raw_value}
    if isinstance(raw_value, (int, float)):
        return {"double_value": float(raw_value)}
    try:
        return {"double_value": float(raw_value)}
    except (TypeError, ValueError):
        return {"string_value": str(raw_value)}


def _map_operator(op_symbol: str) -> str:
    """Translate JSON operator symbol to Alerts v2 ComparisonOperator enum.

    Raises ValueError on unknown symbol — defense-in-depth check that fires
    even if validate_entry() is bypassed.
    """
    if op_symbol not in OPS_MAPPING:
        raise ValueError(
            f"Unknown operator {op_symbol!r}. "
            f"Supported: {sorted(OPS_MAPPING.keys())}"
        )
    return OPS_MAPPING[op_symbol]


def _get_nested(entry: dict, dotted_path: str):
    """Walk a nested dict using a dotted path string.

    Returns the value if found, or None if any level is missing or not a dict.
    Example: _get_nested(entry, "alert.options.op")
    """
    parts = dotted_path.split(".")
    node = entry
    for part in parts:
        if not isinstance(node, dict):
            return None
        node = node.get(part)
        if node is None:
            return None
    return node


def validate_entry(entry: dict) -> None:
    """Validate a single alertable JSON entry against the required schema.

    Raises ValueError with the entry name and the offending field/value so
    callers get an actionable message rather than a KeyError or AttributeError.

    Returns None on success. Callers should invoke this before _build_alert_resource().
    """
    entry_name = entry.get("name", "<unnamed>")

    # Check all required dotted-path fields are present.
    for path in REQUIRED_ALERT_FIELDS:
        if _get_nested(entry, path) is None:
            raise ValueError(
                f"Entry {entry_name!r}: missing required field {path!r}"
            )

    # Check operator is recognised.
    op = entry["alert"]["options"]["op"]
    if op not in OPS_MAPPING:
        raise ValueError(
            f"Entry {entry_name!r}: unknown operator {op!r}. "
            f"Supported: {sorted(OPS_MAPPING.keys())}"
        )

    # Check rearm is a numeric string.
    rearm = entry["alert"]["rearm"]
    try:
        int(rearm)
    except (ValueError, TypeError):
        raise ValueError(
            f"Entry {entry_name!r}: alert.rearm must be a numeric string, got {rearm!r}"
        )


def _build_alert_resource(entry: dict) -> dict:
    """Map one JSON entry (with alert sub-object) to an Alerts v2 resource dict.

    Caller must ensure entry.get('alert') is truthy — query-only entries are
    filtered upstream in generate().
    """
    alert = entry["alert"]
    options = alert["options"]

    pause_status = "PAUSED" if options.get("muted") else "UNPAUSED"

    return {
        "display_name": alert["name"],
        "query_text": entry["query"],
        "warehouse_id": "${var.warehouse_id}",
        "evaluation": {
            "comparison_operator": _map_operator(options["op"]),
            "source": {"name": options["column"]},
            "threshold": {
                "value": _threshold_value(options["value"]),
            },
            # Empty result (no matching audit events) means "nothing to alert
            # on", not an evaluation failure. Default is ERROR, which surfaces
            # every normal empty window as a broken alert in the UI.
            "empty_result_state": "OK",
            "notification": {
                # Driven by the bundle variable, not JSON `rearm`. Default is
                # 0 (notify once). Users who want hourly re-notification can
                # set retrigger_seconds=3600 in variable-overrides.json — no
                # need to touch the legacy JSON `rearm` field, which stays as
                # it is for the notebook + Terraform paths.
                "retrigger_seconds": "${var.retrigger_seconds}",
                # MAP-05: always emit subscriptions, even if the list looks
                # "obvious". Silent omission is Pitfall 8.
                "subscriptions": [
                    {"user_email": "${var.alert_emails}"},
                ],
            },
        },
        "schedule": {
            "quartz_cron_schedule": "${var.alert_schedule}",
            "timezone_id": "${var.alert_timezone}",
            "pause_status": pause_status,
        },
        "custom_description": options.get("custom_body", ""),
        "custom_summary": options.get("custom_subject", ""),
    }


def generate(config_path: Path = None) -> dict:
    """Read JSON config, validate, filter, map — return the resources dict.

    config_path defaults to JSON_CONFIG (the real data file). Tests pass a
    fixture path to keep tests hermetic.

    Separated from the file-writing main() so tests can assert on the dict
    directly without touching disk.
    """
    if config_path is None:
        config_path = JSON_CONFIG

    with open(config_path) as f:
        config = json.load(f)

    if not isinstance(config, dict) or "queries_and_alerts" not in config:
        raise ValueError(
            f"{config_path}: malformed config — expected an object with a "
            f"top-level 'queries_and_alerts' key. Got keys: "
            f"{sorted(config.keys()) if isinstance(config, dict) else type(config).__name__}"
        )

    alerts_out = {}
    for entry in config["queries_and_alerts"]:
        # GEN-03: query-only entries (no `alert` sub-object) are skipped silently.
        if not entry.get("alert"):
            continue

        # GEN-04 / GEN-06: validate before building — raises ValueError with
        # entry name + field path on any schema violation.
        validate_entry(entry)

        # Resource key = JSON entry name. Stable keys prevent orphan alerts on
        # rename (PITFALLS.md Pitfall 10).
        alerts_out[entry["name"]] = _build_alert_resource(entry)

    return {"resources": {"alerts": alerts_out}}


def main() -> int:
    resources = generate()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        # default_flow_style=False keeps the output in block YAML (readable,
        # diff-friendly). sort_keys=False preserves our intentional field order.
        yaml.safe_dump(resources, f, default_flow_style=False, sort_keys=False)

    alert_count = len(resources["resources"]["alerts"])
    print(f"generate_alerts: wrote {alert_count} alerts to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
