# client-02-quotation – HansePack Angebotsrechner

Produkt-Repository für **Kundenprojekt 02 (HansePack)**, Termin 6–8 im Kurs *Agentic AI Software Factory* (HAW Hamburg), Team 3 / PepeGroup.

- Factory: https://github.com/BohdanBerlev/agentic_ai_peppe
- Vorheriges Kundenprojekt (Nordwerk): https://github.com/DavidPisark/Nordwerk-Industrie-Service-Website

## Kundenfixtures (unverändert)

`fixtures/HansePack_Katalog.json` und `fixtures/HansePack_Referenzfaelle.json` sind unveränderte Kopien aus
`MARS-Group-HAW/agentic_ai`, Branch `course/session-03`, Commit `f66013c`, Ordner `task sheets/session-06-08/`.
Herkunftsnachweis: Git-Blob-Hashes identisch mit der Quelle; SHA-256 in `fixtures/SHA256SUMS`
(prüfen mit `shasum -a 256 -c fixtures/SHA256SUMS`).

Diese Dateien werden nicht von Hand geändert.

## Start und Tests

Voraussetzung: Python 3.12. Laufzeit nur Standardbibliothek; `pytest` nur für Tests.

```bash
python -m pip install -r requirements.txt
python quotation.py HP-BOX 50     # Angebot als JSON
python -m pytest -q               # Produkttests (Q01, Q03, E01)
```

Das Produkt läuft ohne Factory und ohne LLM. Spezifikation: `issue_hp01.md`.
