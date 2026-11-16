# HP-01 – Angebotsberechnung HP-BOX (Termin 6)

**Kunde:** HansePack Handelsgesellschaft (fiktiv) · **Projekt:** `client-02` · **Regelversion:** HP-V1
**Quelle:** Kundenbriefing HansePack v1.0 (08.11.2026), `fixtures/HansePack_Katalog.json`, `fixtures/HansePack_Referenzfaelle.json`

## Auftrag für heute
Implementiere in `quotation.py` die deterministische Python-Berechnung für HP-BOX mit Menge 1 und 50 einschließlich Rabatt, Versand und Gesamt. Weise Menge 0 zurück.

## Schnittstelle (verbindlich)
- `calculate_quote(items: list[dict], rule_version: str = "HP-V1") -> dict`
- Eingabe: `[{"sku": "HP-BOX", "quantity": 50}]`
- Ausgabe: `{"lines": [...], "goods_net_cents": int, "shipping_cents": int, "total_cents": int, "currency": "EUR", "rule_version": "HP-V1"}`
- Jede Position in `lines`: `sku`, `quantity`, `unit_price_cents`, `list_amount_cents`, `discount_percent`, `discount_cents`, `net_cents` (gleiche Feldnamen wie die Referenzdatei).
- Ungültige Eingabe: `raise QuotationError(reason, message)`; `QuotationError` erbt von `ValueError` und hat das Attribut `reason` (z. B. `"quantity_out_of_range"`). Kein Angebot wird zurückgegeben.
- Preise kommen aus `fixtures/HansePack_Katalog.json` (relativ zum Ordner von `quotation.py`), nicht hart im Code.
- CLI: `python quotation.py HP-BOX 50` gibt das Angebot als JSON aus; bei Fehler Meldung auf stderr und Exit-Code 1.

## Fachregeln (aus dem Briefing)
1. Geld nur als ganze Cent (`int`), keine Gleitkommazahlen.
2. Listenbetrag = Menge × Einzelpreis.
3. Rabatt auf den ganzen Listenbetrag der Position: 1–49 → 0 %, 50–99 → 5 %, ab 100 → 10 %.
4. Rabattbetrag kaufmännisch gerundet (halber Cent wird aufgerundet), als Ganzzahlformel: `(list_amount_cents * discount_percent + 50) // 100`.
5. Netto = Listenbetrag − Rabattbetrag; Warenwert = Summe Netto.
6. HP-V1: Versand 1200 Cent bei Warenwert < 50000, sonst 0. Gesamt = Warenwert + Versand.
7. Menge muss eine ganze Zahl 1–10.000 sein (`bool` ist ungültig); sonst `QuotationError("quantity_out_of_range", ...)` bzw. `"quantity_wrong_type"` (falscher Typ) oder `"quantity_not_integer"` (keine ganze Zahl).

## Abnahme heute (eigene Produkttests in `test_quotation.py`)
| Fall | Erwartung |
|---|---|
| Q01 HP-BOX × 1 | Warenwert 250, Versand 1200, Gesamt 1450 |
| Q03 HP-BOX × 50 | Listenbetrag 12500, Rabatt 625, Warenwert 11875, Versand 1200, Gesamt 13075 |
| E01 Menge 0 | `QuotationError`, kein Angebot |

## Annahmen
- A1: Für T6 genügt die Python-Funktion mit CLI; Weboberfläche und JSON-Download folgen in T7.
- A2: Feldnamen der Ausgabe entsprechen der Referenzdatei; damit ist keine Zuordnungstabelle nötig.
- A3: Fehler werden als Exception mit semantischem `reason` gemeldet; der genaue Text ist frei.
- A4: Laufzeit nur Python 3.12-Standardbibliothek; `pytest` nur für Tests.
- A5: Produkt läuft ohne Factory und ohne LLM.

## Offene Fragen an den Kunden
- F1: Soll die Weboberfläche (T7) deutsch oder englisch sein? Annahme bis zur Antwort: deutsch.
- F2: Sollen Artikelnamen (`name_de`/`name_en`) im JSON-Export erscheinen oder nur die SKU?
- F3: Gilt die Obergrenze 10.000 je Position oder je Angebot? Annahme: je Position.
- F4: Soll ein Angebot eine Angebotsnummer/Zeitstempel bekommen? Annahme: nein (optional laut Briefing).

## Lieferplan
- T6: Fachlogik Q01, Q03, E01 (HP-AC01 erster Stand, HP-AC02, HP-AC04 Teil).
- T7: alle Q01–Q14 und E01–E10, Weboberfläche, JSON-Export, frischer Checkout, Release Candidate (HP-AC03–07).
- T8: Reserve für Änderung CR-02 (HP-V2 Versand) und Release (HP-AC08–09).

## Verantwortung
- Kunde und Abnahme: Dozent in der Kundenrolle HansePack
- Kunden-Issue und Anforderungen (Product Owner): Mehrose Farooq
- Planung (Project Manager) sowie Produkttests und Freigabe des Produktdiffs (QA): Lars Boos
- Architektur und Integration: David Pisarkiewicz
- Fachlogik (Backend): Maxim Bers
