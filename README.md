# client-02-quotation – HansePack Angebotsrechner (HP-V1)

Eigenständiges Produkt-Repository für **Kundenprojekt 02 (HansePack)**, Termin 6–8 im Kurs *Agentic AI Software Factory* (HAW Hamburg), Team 3 / PepeGroup.

- Factory: https://github.com/BohdanBerlev/agentic_ai_peppe
- Vorheriges Kundenprojekt (Nordwerk): https://github.com/DavidPisark/Nordwerk-Industrie-Service-Website

## Kundenfixtures (unverändert)

`fixtures/HansePack_Katalog.json` und `fixtures/HansePack_Referenzfaelle.json` sind unveränderte Kopien aus
`MARS-Group-HAW/agentic_ai`, Branch `course/session-03`, Commit `f66013c`, Ordner `task sheets/session-06-08/`.
Herkunftsnachweis: Git-Blob-Hashes identisch mit der Quelle; SHA-256 in `fixtures/SHA256SUMS`
(prüfen mit `shasum -a 256 -c fixtures/SHA256SUMS`).

Diese Dateien werden nicht von Hand geändert.

## Voraussetzungen, Start und Tests (ohne Factory & ohne LLM)

Voraussetzung: **Python 3.12+**. Das Produkt benötigt weder Factory noch LLM oder Datenbank.

### 1. Abhängigkeiten installieren
```bash
python -m pip install -r requirements.txt
```

### 2. Weboberfläche starten (FastAPI + JSON-Export)
```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```
Danach im Browser öffnen: `http://127.0.0.1:8000/`

### 3. CLI-Aufruf (direkte Python-Fachlogik)
```bash
python quotation.py HP-BOX 50
```

### 4. Vollständige Produkttests ausführen (Q01–Q14, E01–E10, UI, API & JSON-Export)
```bash
python -m pytest -v
```
