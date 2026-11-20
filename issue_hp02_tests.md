# HP-T7-B-TESTS – Vollständige Fachtest-Suite Q01–Q14, E01–E10 & Export-Konsistenz

**Kunde:** HansePack · **Projekt:** `client-02` · **Regelversion:** `HP-V1` · **Zieldatei:** `test_quotation.py`

## Auftrag
Erweitere `test_quotation.py` so, dass alle vom Kunden vorgegebenen Referenzfälle in `fixtures/HansePack_Referenzfaelle.json` unter `HP-V1` vollständig getestet werden:

1. **Alle 14 gültigen Fälle `Q01`–`Q14` (`B1`, `B2`):**
   - Lade `ALL_VALID_IDS = [c["id"] for c in REF["valid_cases"]]` und parametrisiere `test_valid_case_hp_v1` über alle 14 IDs.
   - Prüfe je Fall `goods_net_cents`, `shipping_cents`, `total_cents`, `currency`, `rule_version` sowie alle Positionsfelder in `lines` (`sku`, `quantity`, `unit_price_cents`, `list_amount_cents`, `discount_percent`, `discount_cents`, `net_cents`).
   - Prüfe, dass alle Cent-Felder exakt vom Typ `int` (`type(val) is int`, kein `bool`) sind.
   - Behalte explizite Prüfungen für `Q03` (13075 Cent), `Q04`/`Q13`/`Q14` (kaufmännische Rundung `ROUND_HALF_UP`: 1238 / 3188 / 663 Cent Rabatt) und `Q06`/`Q07` (Versandschwelle 50000 Cent nach Rabatt).
2. **Alle 10 ungültigen Fälle `E01`–`E10` (`B3`):**
   - Lade `ALL_INVALID_IDS = [c["id"] for c in REF["invalid_cases"]]` und parametrisiere `test_invalid_case_rejected` über alle 10 IDs.
   - Prüfe, dass `calculate_quote(case["input"]["items"], rule_version="HP-V1")` eine `QuotationError` mit `excinfo.value.reason == case["expected_reason"]` und nicht-leerer Meldung wirft.
3. **Export-Konsistenz (`B5`):**
   - Importiere `build_export_payload` und `export_quote_json` aus `quotation`.
   - Prüfe für alle 14 Fälle, dass `json.loads(export_quote_json(result)) == result` und `build_export_payload(result) == result`.
4. **Ausführbarkeit:**
   - Behalte `if __name__ == "__main__": sys.exit(pytest.main(["-q", str(Path(__file__).resolve())]))` am Dateiende.
   - Keine Änderungen an `fixtures/HansePack_Referenzfaelle.json`.
