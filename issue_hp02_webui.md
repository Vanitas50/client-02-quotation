# HP-T7-B-WEBUI – Kleine FastAPI-Weboberfläche & JSON-Export (`app.py`)

**Kunde:** HansePack · **Projekt:** `client-02` · **Regelversion:** `HP-V1` · **Zieldatei:** `app.py`

## Auftrag
Implementiere in `app.py` eine kleine, eigenständig lauffähige FastAPI-Webanwendung (`app = FastAPI(...)`) für den HansePack Angebotsrechner (HP-V1) ohne Datenbank und ohne LLM-Nutzung. Die HTML/CSS/JS-Oberfläche soll direkt als Python-String (`HTML_PAGE`) in `app.py` eingebettet sein und über `GET /` als `HTMLResponse` ausgeliefert werden.

## Verbindliche Anforderungen (HP-AC04, HP-AC05, HP-AC06)
1. **`GET /` (`HTMLResponse`):**
   - Zeigt die gut sichtbare Pflicht-Kennzeichnung exakt: `Nettobeträge – Lehrprojekt, kein verbindliches Angebot`.
   - Erlaubt das Erfassen von 1–3 Positionen (Artikelauswahl geladen aus `/api/catalog` für `HP-BOX`, `HP-TAPE`, `HP-FILM`; Mengenfeld als `type="text"` ohne clientseitige Sperre, damit ungültige Mengen wie `0`, `-1`, `1.5`, `"abc"` die Python-Fachlogik erreichen).
   - Button „Angebot berechnen“ sendet JSON an `POST /api/quote` und zeigt Positionswerte (SKU, Menge, Einzelpreis, Listenbetrag, Rabatt %, Rabattbetrag, Netto), Warenwert, Versand, Gesamt, Währung (`EUR`) und Regelversion (`HP-V1`).
   - Bei Fehler (HTTP 400) wird eine verständliche Fehlermeldung angezeigt und der Ergebnis-/Download-Bereich ausgeblendet (kein scheinbar gültiges Angebot).
   - Button „JSON herunterladen“ ruft `POST /api/quote/export` mit denselben Eingaben auf und lädt `hansepack-angebot-HP-V1.json` herunter.
2. **`GET /api/catalog` (`JSONResponse`):**
   - Nutzt `load_catalog()` aus `quotation.py` und gibt `{"currency": "EUR", "rule_version": "HP-V1", "products": list(catalog.values())}` zurück.
3. **`POST /api/quote` (`JSONResponse`):**
   - **WICHTIG (keine stille Typumwandlung!):** Liest den Body als rohes JSON (`data = json.loads((await request.body()).decode("utf-8"))`), NICHT über Pydantic-Modelle!
   - Übergibt `data["items"]` und `data.get("rule_version", "HP-V1")` unverändert an `calculate_quote(...)` und `build_export_payload(...)` aus `quotation.py`.
   - Bei `QuotationError` (oder ungültigem JSON / fehlendem `items`): HTTP `400` mit `{"error": {"reason": ..., "message": ...}}`.
4. **`POST /api/quote/export` (`Response`):**
   - Parst Roh-JSON identisch zu `POST /api/quote`, berechnet mit `calculate_quote(...)` und serialisiert mit `export_quote_json(...)`.
   - Gibt HTTP `200`, `media_type="application/json; charset=utf-8"` und Header `Content-Disposition: attachment; filename="hansepack-angebot-HP-V1.json"` zurück; bei Fehler HTTP `400`.
