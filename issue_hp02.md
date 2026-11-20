# HP-02 – Konsistenter JSON-Export & vollständige HP-V1-Fachtests (Termin 7)

**Kunde:** HansePack Handelsgesellschaft (fiktiv) · **Projekt:** `client-02` · **Regelversion:** HP-V1  
**Quelle:** Kundenbriefing HansePack v1.0 (08.11.2026), Aufgabenblatt Termin 7, `fixtures/HansePack_Katalog.json`, `fixtures/HansePack_Referenzfaelle.json`

## Auftrag für Termin 7 (Task HP-T7-01)
Erweitere `quotation.py` um eine deterministische JSON-Export-Funktion `build_export_payload(quote: dict) -> dict` und `export_quote_json(quote: dict) -> str`, die aus einem berechneten Angebot exakt den standardkonformen JSON-Export gemäß HP-AC06 erzeugt, ohne die bestehende Preisberechnung (`calculate_quote`), Rundung (`(list_amount_cents * discount_percent + 50) // 100`) oder Validierung (`QuotationError`) zu verändern.

## Verbindliche Anforderungen (HP-AC03, HP-AC04, HP-AC06)
1. **Unveränderte Fachlogik HP-V1:**
   - Alle 14 gültigen Kundenreferenzfälle `Q01`–`Q14` (inkl. Positionswerte, Staffelgrenzen 49/50/99/100, kaufmännische Rundung `Q04`/`Q13`/`Q14`, Versandschwelle `Q06`/`Q07`) bleiben exakt korrekt.
   - Alle 10 ungültigen Fälle `E01`–`E10` werden deterministisch in Python mit `QuotationError` zurückgewiesen (keine stille Typumwandlung oder SKU-Zusammenfassung).
2. **Konsistenter JSON-Export (`quotation.py`):**
   - `build_export_payload(quote: dict) -> dict`: Prüft, dass alle Pflichtfelder vorhanden sind (`lines`, `goods_net_cents`, `shipping_cents`, `total_cents`, `currency`, `rule_version`) und alle Geldwerte ganzzahlige Cent (`int`, kein `bool`) sind. Gibt ein konsistentes Dictionary zurück.
   - `export_quote_json(quote: dict) -> str`: Serialisiert `build_export_payload(quote)` deterministisch als UTF-8 JSON (`json.dumps(..., indent=2, ensure_ascii=False)`).
   - Die CLI (`main()`) nutzt `export_quote_json(quote)` für die Ausgabe, sodass CLI, Anzeige und Download dieselben berechneten Daten verwenden.
3. **Abgrenzung:**
   - Regelversion bleibt strikt `HP-V1` (kein `HP-V2` / CR-02 vorwegnehmen).
   - Keine Laufzeitabhängigkeit zur Factory und kein LLM im Produkt.

## Abnahmekriterien
- `python -m pytest -q` im Produkt-Repo besteht vollständig.
- `build_export_payload` und `export_quote_json` sind in `quotation.py` implementiert und liefern exakt die berechneten Integer-Cent-Werte und `rule_version == "HP-V1"`.
