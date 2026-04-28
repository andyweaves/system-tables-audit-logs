"""Tests for bundle/src/generate_alerts.py.

Covers: operator mapping (all 6), retrigger_seconds bundle-variable
reference, query-only skip, unknown-operator error, missing-required-field
error, muted -> pause_status, notification subscriptions always emitted,
Alerts v2 schema correctness (double_value thresholds, empty_result_state),
malformed config rejection, and a real-config smoke test.

Run from repo root:
    python3 -m pytest bundle/tests/ -v
"""

from pathlib import Path

import pytest

from bundle.src.generate_alerts import (
    OPS_MAPPING,
    REQUIRED_ALERT_FIELDS,
    _build_alert_resource,
    _get_nested,
    _map_operator,
    generate,
    validate_entry,
)

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Test 1: All 6 operators map to the correct Alerts v2 enum
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("symbol,expected", [
    (">",  "GREATER_THAN"),
    (">=", "GREATER_THAN_OR_EQUAL"),
    ("<",  "LESS_THAN"),
    # regression guard: notebooks/functions.py:74 maps <= to LESS_THAN (bug)
    ("<=", "LESS_THAN_OR_EQUAL"),
    ("==", "EQUAL"),
    ("!=", "NOT_EQUAL"),
])
def test_operator_mapping_all_six(symbol, expected):
    assert _map_operator(symbol) == expected
    assert OPS_MAPPING[symbol] == expected


# ---------------------------------------------------------------------------
# Test 2: Unknown operator raises ValueError
# ---------------------------------------------------------------------------

def test_unknown_operator_raises_valueerror():
    with pytest.raises(ValueError, match=r"~="):
        _map_operator("~=")


def test_unknown_operator_message_includes_supported_list():
    with pytest.raises(ValueError, match=r"Supported"):
        _map_operator("~=")


def test_unknown_operator_in_full_config_raises():
    with pytest.raises(ValueError, match="unknown operator"):
        generate(config_path=FIXTURES / "unknown_operator.json")


# ---------------------------------------------------------------------------
# Test 3: retrigger_seconds driven by bundle variable; validate_entry still
# enforces JSON `rearm` is numeric (shared schema with notebook/TF paths)
# ---------------------------------------------------------------------------

def test_retrigger_seconds_references_bundle_variable():
    """Generator emits ${var.retrigger_seconds} — NOT the JSON rearm field.

    Default is 0 (notify once); users override via variable-overrides.json.
    The JSON rearm stays untouched for the notebook and Terraform paths.
    """
    resources = generate(config_path=FIXTURES / "valid_entry.json")
    alert = resources["resources"]["alerts"]["fixture_valid"]
    retrig = alert["evaluation"]["notification"]["retrigger_seconds"]
    assert retrig == "${var.retrigger_seconds}"


def test_rearm_non_numeric_raises_valueerror():
    entry = {
        "name": "bad_rearm",
        "query": "SELECT 1",
        "alert": {
            "name": "bad_rearm",
            "rearm": "not-a-number",
            "options": {"column": "total", "op": ">", "value": "0"},
        },
    }
    with pytest.raises(ValueError, match="rearm"):
        validate_entry(entry)


# ---------------------------------------------------------------------------
# Test 4: Query-only entries are silently skipped (no error, no warning)
# ---------------------------------------------------------------------------

def test_query_only_entries_silently_skipped():
    resources = generate(config_path=FIXTURES / "query_only_entry.json")
    alerts = resources["resources"]["alerts"]
    # fixture has one alertable (key="fixture_valid") + one query-only (key="fixture_query_only")
    # Resource key is the JSON entry 'name' field, not the alert display_name.
    assert len(alerts) == 1
    assert "fixture_valid" in alerts
    # query-only entry must NOT appear
    assert not any("query_only" in k for k in alerts)


# ---------------------------------------------------------------------------
# Test 5: Missing required field raises ValueError with entry name + path
# ---------------------------------------------------------------------------

def test_missing_required_field_raises():
    with pytest.raises(ValueError, match="alert.options.op"):
        generate(config_path=FIXTURES / "missing_required_field.json")


def test_missing_required_field_includes_entry_name():
    with pytest.raises(ValueError, match="fixture_missing_op"):
        generate(config_path=FIXTURES / "missing_required_field.json")


# ---------------------------------------------------------------------------
# Test 6: muted -> pause_status mapping
# ---------------------------------------------------------------------------

def test_muted_false_produces_unpaused():
    entry = {
        "name": "x",
        "query": "SELECT 1",
        "alert": {
            "name": "x",
            "rearm": "3600",
            "options": {"column": "total", "op": ">", "value": "0", "muted": False},
        },
    }
    result = _build_alert_resource(entry)
    assert result["schedule"]["pause_status"] == "UNPAUSED"


def test_muted_true_produces_paused():
    entry = {
        "name": "x",
        "query": "SELECT 1",
        "alert": {
            "name": "x",
            "rearm": "3600",
            "options": {"column": "total", "op": ">", "value": "0", "muted": True},
        },
    }
    result = _build_alert_resource(entry)
    assert result["schedule"]["pause_status"] == "PAUSED"


def test_muted_absent_produces_unpaused():
    entry = {
        "name": "x",
        "query": "SELECT 1",
        "alert": {
            "name": "x",
            "rearm": "3600",
            "options": {"column": "total", "op": ">", "value": "0"},
        },
    }
    result = _build_alert_resource(entry)
    assert result["schedule"]["pause_status"] == "UNPAUSED"


# ---------------------------------------------------------------------------
# Test 7: Notification subscriptions always emitted (Pitfall 8 regression guard)
# ---------------------------------------------------------------------------

def test_notification_subscriptions_always_emitted():
    resources = generate(config_path=FIXTURES / "valid_entry.json")
    for alert_key, alert in resources["resources"]["alerts"].items():
        subs = alert["evaluation"]["notification"]["subscriptions"]
        assert isinstance(subs, list) and len(subs) >= 1, (
            f"Alert {alert_key!r} has empty/missing subscriptions — Pitfall 8"
        )


# ---------------------------------------------------------------------------
# Helper: _get_nested
# ---------------------------------------------------------------------------

def test_get_nested_returns_value():
    entry = {"alert": {"options": {"op": ">"}}}
    from bundle.src.generate_alerts import _get_nested
    assert _get_nested(entry, "alert.options.op") == ">"


def test_get_nested_returns_none_for_missing():
    entry = {"alert": {"options": {}}}
    from bundle.src.generate_alerts import _get_nested
    assert _get_nested(entry, "alert.options.op") is None


def test_get_nested_returns_none_for_non_dict_node():
    entry = {"alert": "not-a-dict"}
    from bundle.src.generate_alerts import _get_nested
    assert _get_nested(entry, "alert.options.op") is None


# ---------------------------------------------------------------------------
# Helper: REQUIRED_ALERT_FIELDS completeness check
# ---------------------------------------------------------------------------

def test_required_alert_fields_includes_all_seven():
    # Ensure the constant covers all 7 required paths from the plan spec
    expected_paths = {
        "name", "query",
        "alert.name", "alert.rearm",
        "alert.options.op", "alert.options.column", "alert.options.value",
    }
    assert expected_paths == set(REQUIRED_ALERT_FIELDS)


# ---------------------------------------------------------------------------
# Test 8: Alerts v2 schema correctness — regression guards for the two
# schema bugs surfaced and fixed during Phase 1 end-to-end deploy validation
# ---------------------------------------------------------------------------

def test_threshold_numeric_string_emits_double_value():
    """Alerts v2 rejects string_value thresholds when the source column is
    numeric (e.g. COUNT aggregates). All thresholds in the real config are
    numeric counts/sums stored as JSON strings. Generator must wrap them as
    double_value, not string_value. Regression guard for commit 9f2938d."""
    resources = generate(config_path=FIXTURES / "valid_entry.json")
    threshold = resources["resources"]["alerts"]["fixture_valid"]["evaluation"]["threshold"]
    assert threshold["value"] == {"double_value": 0.0}


def test_threshold_value_helper_packs_typed_wrappers():
    """Direct unit coverage of _threshold_value() — bool, int/float, numeric
    string, and non-numeric string fallback paths."""
    from bundle.src.generate_alerts import _threshold_value

    assert _threshold_value(True) == {"bool_value": True}
    assert _threshold_value(False) == {"bool_value": False}
    assert _threshold_value(5) == {"double_value": 5.0}
    assert _threshold_value(3.14) == {"double_value": 3.14}
    assert _threshold_value("42") == {"double_value": 42.0}
    assert _threshold_value("not-numeric") == {"string_value": "not-numeric"}


def test_empty_result_state_is_ok_for_every_alert():
    """Alerts v2 defaults empty_result_state to ERROR. Most audit alerts
    return zero rows in the healthy state, so the default surfaces every
    healthy window as a broken alert. Generator must explicitly set OK on
    every alert. Regression guard for commit cee90db."""
    resources = generate(config_path=FIXTURES / "valid_entry.json")
    for alert_key, alert in resources["resources"]["alerts"].items():
        assert alert["evaluation"]["empty_result_state"] == "OK", (
            f"Alert {alert_key!r} missing or wrong empty_result_state — "
            f"would surface healthy zero-row results as evaluation errors"
        )


# ---------------------------------------------------------------------------
# Test 9: Malformed top-level config produces an actionable ValueError,
# not a bare KeyError or AttributeError
# ---------------------------------------------------------------------------

def test_malformed_top_level_raises_clean_valueerror():
    """If someone hand-edits the JSON and breaks the top-level shape, the
    generator should fail with an actionable error message naming the
    expected key — not a Python traceback that leaves users guessing."""
    with pytest.raises(ValueError, match="queries_and_alerts"):
        generate(config_path=FIXTURES / "malformed_top_level.json")


def test_malformed_top_level_message_lists_actual_keys():
    """Error message should help the user see what they DO have so they
    can correct it."""
    with pytest.raises(ValueError, match="wrong_top_key"):
        generate(config_path=FIXTURES / "malformed_top_level.json")


# ---------------------------------------------------------------------------
# Test 10: Smoke test against the real shipped config — catches JSON drift
# (typos, removed fields, new operators we forgot to map) without requiring
# a workspace deploy
# ---------------------------------------------------------------------------

def test_real_config_generates_without_errors():
    """The committed resources/queries_and_alerts.json must always pass
    through the full generate() pipeline cleanly. If a contributor adds an
    alert with a typo or unknown operator, this test fails fast at PR time
    instead of at deploy time."""
    resources = generate()  # default path = real shipped config
    alerts = resources["resources"]["alerts"]
    # Pin a lower bound — current count is 30; alerts can be added but not
    # silently dropped en masse (which would mean a JSON-shape regression).
    assert len(alerts) >= 30, (
        f"Real config generated only {len(alerts)} alerts; expected >= 30. "
        f"Has the JSON shape changed, or have alertable entries been removed?"
    )


def test_real_config_every_alert_has_subscriptions_and_ok_empty_state():
    """Combined Pitfall-8 + empty_result_state regression check against the
    real shipped config. If either ever regresses, every alert in production
    breaks — this catches it before deploy."""
    resources = generate()
    for alert_key, alert in resources["resources"]["alerts"].items():
        evaluation = alert["evaluation"]
        assert evaluation["empty_result_state"] == "OK", alert_key
        subs = evaluation["notification"]["subscriptions"]
        assert isinstance(subs, list) and len(subs) >= 1, alert_key
