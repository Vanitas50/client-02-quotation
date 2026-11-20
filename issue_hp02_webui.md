# HP-T7-B-API – FastAPI-Backend & JSON-Export (`app.py`)

**Kunde:** HansePack · **Projekt:** `client-02` · **Regelversion:** `HP-V1` · **Zieldatei:** `app.py`

## Auftrag
Implementiere in `app.py` eine kompakte, saubere FastAPI-App (`app = FastAPI(title="HansePack Angebotsrechner (HP-V1)")`) ohne eingebettetes HTML (sie lädt `Path(__file__).resolve().parent / "static" / "index.html"`).

## Endpunkte (verbindlich)
1. `GET /` (`HTMLResponse`): Liest `static/index.html` (UTF-8) und gibt sie als `HTMLResponse` zurück.
2. `GET /api/catalog` (`JSONResponse`): Ruft `load_catalog()` aus `quotation.py` auf und gibt `{"currency": "EUR", "rule_version": "HP-V1", "products": list(catalog.values())}` zurück.
3. `POST /api/quote` (`JSONResponse`):
   - Parst Roh-JSON manuell (`data = json.loads((await request.body()).decode("utf-8"))`), KEIN Pydantic-Modell (damit Strings/Floats/Booleans nicht still umgewandelt werden!).
   - Prüft, dass `data` ein `dict` ist und `"items"` enthält; liest `rule_version = data.get("rule_version", "HP-V1")`.
   - Ruft `calculate_quote(data["items"], rule_version=rule_version)` und `build_export_payload(quote)` auf → HTTP `200` mit diesem Dict.
   - Bei `QuotationError` oder ungültigem JSON: HTTP `400` mit `{"error": {"reason": ..., "message": ...}}`.
4. `POST /api/quote/export` (`Response`):
   - Parst Roh-JSON identisch, ruft `calculate_quote(...)` und `export_quote_json(quote)` auf.
   - Gibt HTTP `200`, `media_type="application/json; charset=utf-8"` und Header `Content-Disposition: attachment; filename="hansepack-angebot-HP-V1.json"` zurück.
   - Bei Fehler: HTTP `400` mit `{"error": {"reason": ..., "message": ...}}`.
