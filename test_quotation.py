"""Eigene Produktchecks gegen die Kundenreferenzdatei (nicht gegen Agentenaussagen).

Aufruf: python -m pytest -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from quotation import QuotationError, calculate_quote

HERE = Path(__file__).resolve().parent
REF = json.loads((HERE / "fixtures" / "HansePack_Referenzfaelle.json").read_text(encoding="utf-8"))
VALID = {c["id"]: c for c in REF["valid_cases"]}
INVALID = {c["id"]: c for c in REF["invalid_cases"]}


@pytest.mark.parametrize("case_id", ["Q01", "Q03"])
def test_valid_case_hp_v1(case_id):
    case = VALID[case_id]
    result = calculate_quote(case["input"]["items"], rule_version="HP-V1")
    exp = case["expected"]["HP-V1"]
    assert result["goods_net_cents"] == exp["goods_net_cents"]
    assert result["shipping_cents"] == exp["shipping_cents"]
    assert result["total_cents"] == exp["total_cents"]
    assert result["currency"] == exp["currency"]
    assert result["rule_version"] == exp["rule_version"]
    assert len(result["lines"]) == len(case["expected_lines"])
    for got, want in zip(result["lines"], case["expected_lines"]):
        for key, value in want.items():
            assert got[key] == value, f"{case_id} {key}: {got[key]!r} != {value!r}"
    for key in ("goods_net_cents", "shipping_cents", "total_cents"):
        assert type(result[key]) is int


def test_q03_explicit_values():
    """Q03 aus dem Aufgabenblatt Termin 6, unabhängig von der Referenzdatei ausgeschrieben."""
    result = calculate_quote([{"sku": "HP-BOX", "quantity": 50}])
    line = result["lines"][0]
    assert line["list_amount_cents"] == 12500
    assert line["discount_cents"] == 625
    assert result["goods_net_cents"] == 11875
    assert result["shipping_cents"] == 1200
    assert result["total_cents"] == 13075


def test_e01_quantity_zero_rejected():
    case = INVALID["E01"]
    with pytest.raises(QuotationError) as excinfo:
        calculate_quote(case["input"]["items"])
    assert excinfo.value.reason == case["expected_reason"]
    assert str(excinfo.value)


if __name__ == "__main__":
    sys.exit(pytest.main(["-q", str(Path(__file__).resolve())]))
