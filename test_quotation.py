"""Eigene Produktchecks gegen die Kundenreferenzdatei (nicht gegen Agentenaussagen).

Aufruf: python -m pytest -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from quotation import QuotationError, calculate_quote, build_export_payload, export_quote_json

HERE = Path(__file__).resolve().parent
REF = json.loads((HERE / "fixtures" / "HansePack_Referenzfaelle.json").read_text(encoding="utf-8"))
VALID = {c["id"]: c for c in REF["valid_cases"]}
INVALID = {c["id"]: c for c in REF["invalid_cases"]}

ALL_VALID_IDS = [c["id"] for c in REF["valid_cases"]]
ALL_INVALID_IDS = [c["id"] for c in REF["invalid_cases"]]


@pytest.mark.parametrize("case_id", ALL_VALID_IDS)
def test_valid_case_hp_v1(case_id):
    case = VALID[case_id]
    result = calculate_quote(case["input"]["items"], rule_version="HP-V1")
    exp = case["expected"]["HP-V1"]
    
    # Check top-level fields
    assert result["goods_net_cents"] == exp["goods_net_cents"]
    assert result["shipping_cents"] == exp["shipping_cents"]
    assert result["total_cents"] == exp["total_cents"]
    assert result["currency"] == exp["currency"]
    assert result["rule_version"] == exp["rule_version"]
    
    # Check lines count
    assert len(result["lines"]) == len(case["expected_lines"])
    
    for got, want in zip(result["lines"], case["expected_lines"]):
        for key, value in want.items():
            assert got[key] == value, f"{case_id} {key}: {got[key]!r} != {value!r}"
    
    # Explicit type checks for monetary values (must be int, not bool)
    for key in ("goods_net_cents", "shipping_cents", "total_cents"):
        assert type(result[key]) is int


@pytest.mark.parametrize("case_id", ALL_INVALID_IDS)
def test_invalid_case_rejected(case_id):
    case = INVALID[case_id]
    with pytest.raises(QuotationError) as excinfo:
        calculate_quote(case["input"]["items"])
    assert excinfo.value.reason == case["expected_reason"]
    assert str(excinfo.value)


@pytest.mark.parametrize("case_id", ALL_VALID_IDS)
def test_export_consistency(case_id):
    case = VALID[case_id]
    result = calculate_quote(case["input"]["items"], rule_version="HP-V1")
    
    # Check JSON export consistency
    json_str = export_quote_json(result)
    assert json.loads(json_str) == result, f"Export JSON mismatch for {case_id}"
    
    # Check payload builder consistency
    payload = build_export_payload(result)
    assert payload == result, f"Payload builder mismatch for {case_id}"


if __name__ == "__main__":
    sys.exit(pytest.main(["-q", str(Path(__file__).resolve())]))