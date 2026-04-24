"""Tests for bundle/src/generate_alerts.py.

Covers GEN-08 checklist: operator mapping (all 6), rearm int cast,
query-only skip, unknown-operator error, missing-required-field error,
muted -> pause_status, and notification subscriptions always emitted.

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
# Test 3: rearm int cast — happy path and bad path
# ---------------------------------------------------------------------------

def test_rearm_is_cast_to_int():
    resources = generate(config_path=FIXTURES / "valid_entry.json")
    # Resource key is the JSON entry 'name' field ("fixture_valid"), not the alert name.
    alert = resources["resources"]["alerts"]["fixture_valid"]
    retrig = alert["evaluation"]["notification"]["retrigger_seconds"]
    assert isinstance(retrig, int)
    assert retrig == 3600


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
