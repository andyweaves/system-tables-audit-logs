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
    "<=": "LESS_THAN_OR_EQUAL",
    "==": "EQUAL",
    "!=": "NOT_EQUAL",
}


def _map_operator(op_symbol: str) -> str:
    """Translate JSON operator symbol to Alerts v2 ComparisonOperator enum.

    Raises ValueError on unknown symbol — plan 01-04 adds the dedicated
    validation path and tests for this.
    """
    if op_symbol not in OPS_MAPPING:
        raise ValueError(
            f"Unknown operator {op_symbol!r}. "
            f"Supported: {sorted(OPS_MAPPING.keys())}"
        )
    return OPS_MAPPING[op_symbol]


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
                "value": {"string_value": str(options["value"])},
            },
            "notification": {
                # Cast string rearm ("3600") to int — GEN-07.
                "retrigger_seconds": int(alert["rearm"]),
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


def generate() -> dict:
    """Read JSON config, filter, map — return the resources dict.

    Separated from the file-writing main() so tests can assert on the dict
    directly without touching disk.
    """
    with open(JSON_CONFIG) as f:
        config = json.load(f)

    alerts_out = {}
    for entry in config["queries_and_alerts"]:
        # GEN-03: query-only entries (no `alert` sub-object) are skipped silently.
        if not entry.get("alert"):
            continue

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
