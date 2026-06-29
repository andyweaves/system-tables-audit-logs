"""Preinit generator: reads resources/queries_and_alerts.json and writes
bundle/generated/alerts.yml with one Alerts v2 resource per alertable entry.

This script is invoked by `experimental.scripts.preinit` in bundle/databricks.yml
before `databricks bundle validate` or `databricks bundle deploy`.

Design notes:
- Operator map sourced from terraform/sql.tf, NOT notebooks/functions.py:74,
  which has a known bug mapping `<=` to LESS_THAN instead of LESS_THAN_OR_EQUAL.
- Every alert emits a notification.subscriptions block unconditionally. The
  most insidious failure mode is "alert deploys and fires but no email is
  sent" because subscriptions were silently omitted; an unconditional emit
  rules that out by construction.
- Variable references (${var.*}) are emitted as literal strings. The DAB CLI
  resolves them at deploy time; this generator never sees real values.
"""

import json
import math
import sys
from pathlib import Path

import yaml

# Paths relative to repo root (the bundle root — see bundle/databricks.yml).
REPO_ROOT = Path(__file__).resolve().parents[2]
JSON_CONFIG = REPO_ROOT / "resources" / "queries_and_alerts.json"
OUTPUT_DIR = REPO_ROOT / "bundle" / "generated"
OUTPUT_FILE = OUTPUT_DIR / "alerts.yml"

# Sourced from terraform/sql.tf (verified against CLI 0.288.0 bundle schema).
# Regression guard on `<=`: notebooks/functions.py:74 maps it to LESS_THAN
# (a bug); we map to LESS_THAN_OR_EQUAL (correct).
OPS_MAPPING = {
    ">": "GREATER_THAN",
    ">=": "GREATER_THAN_OR_EQUAL",
    "<": "LESS_THAN",
    "<=": "LESS_THAN_OR_EQUAL",
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


def _threshold_value(raw_value, entry_name: str = "<unnamed>"):
    """Pack a raw JSON threshold value into the Alerts v2 typed wrapper.

    Alerts v2 rejects `string_value` thresholds when the source column is
    numeric (e.g. COUNT aggregates return BIGINT) with
    "Incompatible type in alert evaluation" / INVALID_PARAMETER_VALUE.
    All thresholds in queries_and_alerts.json are numeric counts/sums stored
    as JSON strings; cast to double when parseable, otherwise fall back to
    string.

    Non-finite numeric thresholds (NaN, Infinity) are rejected with a
    ValueError naming the entry: a NaN/Inf comparison threshold can never
    evaluate sensibly and almost always signals a corrupted config. (The
    JSON load also rejects NaN/Infinity tokens up front via parse_constant,
    so these only arise from native float() coercion of an out-of-range
    numeric string such as "1e9999".)
    """
    if isinstance(raw_value, bool):
        return {"bool_value": raw_value}
    if isinstance(raw_value, (int, float)):
        if not math.isfinite(raw_value):
            raise ValueError(
                f"Entry {entry_name!r}: non-finite threshold value {raw_value!r} "
                f"(NaN/Infinity not allowed)"
            )
        return {"double_value": float(raw_value)}
    try:
        coerced = float(raw_value)
    except (TypeError, ValueError):
        return {"string_value": str(raw_value)}
    if not math.isfinite(coerced):
        raise ValueError(
            f"Entry {entry_name!r}: non-finite threshold value {raw_value!r} "
            f"(NaN/Infinity not allowed)"
        )
    return {"double_value": coerced}


def _map_operator(op_symbol: str) -> str:
    """Translate JSON operator symbol to Alerts v2 ComparisonOperator enum.

    Raises ValueError on unknown symbol — defense-in-depth check that fires
    even if validate_entry() is bypassed.
    """
    if op_symbol not in OPS_MAPPING:
        raise ValueError(
            f"Unknown operator {op_symbol!r}. Supported: {sorted(OPS_MAPPING.keys())}"
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
            raise ValueError(f"Entry {entry_name!r}: missing required field {path!r}")

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
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Entry {entry_name!r}: alert.rearm must be a numeric string, got {rearm!r}"
        ) from exc


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
                "value": _threshold_value(
                    options["value"], entry.get("name", "<unnamed>")
                ),
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
                # Always emit subscriptions, unconditionally. An alert with no
                # subscriptions deploys cleanly, transitions to TRIGGERED in
                # the UI, and sends no email — a silent failure mode that's
                # only caught by humans noticing the missing alert. Avoid by
                # construction: never gate this block on any input check.
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


def generate(config_path: Path | None = None) -> dict:
    """Read JSON config, validate, filter, map — return the resources dict.

    config_path defaults to JSON_CONFIG (the real data file). Tests pass a
    fixture path to keep tests hermetic.

    Separated from the file-writing main() so tests can assert on the dict
    directly without touching disk.
    """
    if config_path is None:
        config_path = JSON_CONFIG

    # encoding="utf-8" — Windows defaults to the system locale (e.g.
    # cp1252) and the JSON contains non-ASCII characters in some custom
    # body templates. Explicit UTF-8 keeps the read identical across
    # macOS, Linux, and Windows.
    # parse_constant rejects the non-standard JSON tokens NaN, Infinity, and
    # -Infinity that Python's json module accepts by default. A threshold of
    # Infinity can never evaluate sensibly; fail loud at load time rather than
    # let it flow into a double_value wrapper.
    def _reject_constant(token):
        raise ValueError(
            f"{config_path}: non-standard JSON constant {token!r} is not allowed "
            f"(NaN/Infinity)"
        )

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f, parse_constant=_reject_constant)

    if not isinstance(config, dict) or "queries_and_alerts" not in config:
        actual = (
            sorted(config.keys()) if isinstance(config, dict) else type(config).__name__
        )
        raise ValueError(
            f"{config_path}: malformed config — expected an object with a "
            f"top-level 'queries_and_alerts' key. Got: {actual}"
        )

    # The top-level value must be a list of dict entries. Validate the shape
    # before iterating so a non-list (e.g. a dict or string) or a non-dict
    # item fails with an actionable message instead of an opaque AttributeError
    # when .get(...) is called on it below.
    entries = config["queries_and_alerts"]
    if not isinstance(entries, list):
        raise ValueError(
            f"{config_path}: 'queries_and_alerts' must be a list, got "
            f"{type(entries).__name__}"
        )

    alerts_out = {}
    seen_names = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(
                f"{config_path}: 'queries_and_alerts'[{index}] must be a dict, "
                f"got {type(entry).__name__}"
            )

        # Query-only entries (the `alert` key is ABSENT) are valid in the JSON
        # schema — they predate the alerting feature. Skip them silently.
        # A present `alert` key, however, MUST be a non-empty dict: a
        # present-but-falsy/malformed value ({}, null, a string) is a config
        # error, not a query-only entry, so fail loud rather than silently
        # dropping the alert.
        if "alert" not in entry:
            continue
        alert = entry["alert"]
        if not isinstance(alert, dict) or not alert:
            raise ValueError(
                f"'queries_and_alerts'[{index}] (name="
                f"{entry.get('name', '<unnamed>')!r}): 'alert' key is present but "
                f"is not a non-empty dict (got {alert!r}). Omit the key entirely "
                f"for a query-only entry."
            )

        # Validate before building so callers see a clear ValueError with
        # entry name + field path, not a downstream KeyError or AttributeError.
        validate_entry(entry)

        # Resource key = JSON entry `name`. Renaming a JSON entry deletes the
        # old DAB resource and creates a new one rather than updating in place.
        # That's intentional — Alerts v2 uses display_name as identity from
        # the user's perspective, but DAB needs a stable key, and the JSON
        # entry name is the most stable thing we have.
        name = entry["name"]
        if name in seen_names:
            raise ValueError(
                f"{config_path}: duplicate entry name {name!r} at "
                f"'queries_and_alerts'[{index}] (first seen at index "
                f"{seen_names[name]}). Resource keys must be unique."
            )
        seen_names[name] = index
        alerts_out[name] = _build_alert_resource(entry)

    return {"resources": {"alerts": alerts_out}}


def main() -> int:
    resources = generate()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # encoding="utf-8" + newline="" — write LF-only, UTF-8 output regardless
    # of platform. Without newline="", Windows text mode rewrites \n -> \r\n
    # and YAML diffs become noisy across machines.
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        # default_flow_style=False keeps the output in block YAML (readable,
        # diff-friendly). sort_keys=False preserves our intentional field order.
        yaml.safe_dump(resources, f, default_flow_style=False, sort_keys=False)

    alert_count = len(resources["resources"]["alerts"])
    print(f"generate_alerts: wrote {alert_count} alerts to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
