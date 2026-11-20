"""API-, UI- und JSON-Export-Tests für die HansePack Webanwendung (app.py + static/index.html)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import app
from quotation import calculate_quote, export_quote_json

HERE = Path(__file__).resolve().parent
REF = json.loads((HERE / "fixtures" / "HansePack_Referenzfaelle.json").read_text(encoding="utf-8"))
VALID = {c["id"]: c for c in REF["valid_cases"]}
INVALID = {c["id"]: c for c in REF["invalid_cases"]}

client = TestClient(app)


def test_ui_index_contains_net_notice():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Nettobeträge – Lehrprojekt, kein verbindliches Angebot" in resp.text
    assert "HansePack Angebotsrechner" in resp.text


def test_catalog_endpoint():
    resp = client.get("/api/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert {p["sku"] for p in data["products"]} == {"HP-BOX", "HP-TAPE", "HP-FILM"}
    assert data["rule_version"] == "HP-V1"


@pytest.mark.parametrize("case_id", [c["id"] for c in REF["valid_cases"]])
def test_api_quote_and_export_consistent(case_id: str):
    case = VALID[case_id]
    body = {"items": case["input"]["items"], "rule_version": "HP-V1"}

    r_quote = client.post("/api/quote", json=body)
    assert r_quote.status_code == 200
    quote_data = r_quote.json()

    r_export = client.post("/api/quote/export", json=body)
    assert r_export.status_code == 200
    assert "attachment" in r_export.headers.get("content-disposition", "")
    assert "application/json" in r_export.headers.get("content-type", "")
    export_data = json.loads(r_export.text)

    direct = calculate_quote(case["input"]["items"], rule_version="HP-V1")
    assert quote_data == direct
    assert export_data == quote_data
    assert r_export.text == export_quote_json(direct)


@pytest.mark.parametrize("case_id", [c["id"] for c in REF["invalid_cases"]])
def test_api_rejects_invalid_cases_without_coercion(case_id: str):
    case = INVALID[case_id]
    body = {"items": case["input"]["items"], "rule_version": "HP-V1"}

    r_quote = client.post("/api/quote", json=body)
    assert r_quote.status_code == 400
    assert "error" in r_quote.json()
    assert "total_cents" not in r_quote.json()

    r_export = client.post("/api/quote/export", json=body)
    assert r_export.status_code == 400
