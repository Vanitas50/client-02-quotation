# HP-T7-B-HTML – Kleine Weboberfläche (`static/index.html`)

**Kunde:** HansePack · **Projekt:** `client-02` · **Regelversion:** `HP-V1` · **Zieldatei:** `static/index.html`

## Auftrag
Implementiere in `static/index.html` eine kompakte, saubere, eigenständige HTML5-Seite mit eingebettetem minimalen `<style>` und `<script>` (insgesamt kompakt halten, ca. 100–150 Zeilen, keine externen CDNs/Frameworks).

## Verbindliche Anforderungen (HP-AC05, HP-AC06)
1. **Pflicht-Nettohinweis (wörtlich sichtbar):**
   `Nettobeträge – Lehrprojekt, kein verbindliches Angebot`
2. **Positionserfassung (1–3 Positionen):**
   - Lädt beim Start `/api/catalog` und füllt `<select>` mit `HP-BOX`, `HP-TAPE`, `HP-FILM`.
   - Mengen-Eingabefeld als `<input type="text">` (NICHT `type="number"`, damit ungültige Eingaben wie `0`, `-1`, `1.5`, `"abc"` ans Python-Backend geschickt werden).
   - Buttons: „+ Position“ (max. 3 Zeilen), „Entfernen“ je Zeile, „Angebot berechnen“.
3. **Berechnung (`POST /api/quote`):**
   - Sendet `{"items": [...], "rule_version": "HP-V1"}` (reine Ganzzahlen als `Number`, Dezimalzahlen als `Number`, sonst String).
   - Bei HTTP 200: Zeigt Tabelle mit allen Positionswerten (`sku`, `quantity`, `unit_price_cents`, `list_amount_cents`, `discount_percent`, `discount_cents`, `net_cents`) sowie `goods_net_cents`, `shipping_cents`, `total_cents`, `currency` (`EUR`), `rule_version` (`HP-V1`) und aktiviert Button „JSON herunterladen“.
   - Bei HTTP 400: Blendet den Ergebnis-/Download-Bereich aus und zeigt die verständliche Fehlermeldung aus `data.error.message` an.
4. **JSON-Download (`POST /api/quote/export`):**
   - Button „JSON herunterladen“ ruft `POST /api/quote/export` mit denselben Eingabedaten auf und speichert die Antwort als `hansepack-angebot-HP-V1.json`.
