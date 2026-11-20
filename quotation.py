from __future__ import annotations
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP


class QuotationError(ValueError):
    """Ungültige Angebotseingabe. `reason` ist ein semantischer Fehlercode."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason
        self.message = message


def load_catalog() -> dict[str, dict]:
    """Lädt den Katalog aus fixtures/HansePack_Katalog.json."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    catalog_path = os.path.join(script_dir, "fixtures", "HansePack_Katalog.json")
    
    if not os.path.exists(catalog_path):
        raise FileNotFoundError(f"Katalog nicht gefunden: {catalog_path}")
    
    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Build lookup dict mapping sku to product dict
    products_by_sku = {p['sku']: p for p in data.get('products', [])}
    return products_by_sku


def calculate_quote(items: list[dict], rule_version: str = "HP-V1") -> dict:
    """
    Berechnet das Angebot basierend auf den Artikeln und der Regelversion.
    
    Args:
        items: Liste von Dictionaries mit 'sku' und 'quantity'.
        rule_version: Version der Preisregeln (Standard: HP-V1).
    
    Returns:
        Dictionary mit dem Angebotsresultat.
    
    Raises:
        QuotationError: Bei ungültiger Eingabe.
    """
    # Validierung der Regelversion
    if rule_version != "HP-V1":
        raise QuotationError(
            reason="invalid_rule_version",
            message=f"Ungültige Regelversion: {rule_version}. Nur HP-V1 unterstützt."
        )
    
    # Laden des Katalogs (returns products_by_sku dict)
    try:
        catalog = load_catalog()
    except FileNotFoundError as e:
        raise QuotationError(
            reason="catalog_not_found",
            message=str(e)
        ) from e
    
    if not isinstance(items, list):
        raise QuotationError(
            reason="invalid_items_type",
            message="items muss eine Liste sein."
        )

    if len(items) == 0:
        raise QuotationError(
            reason="empty_items",
            message="Das Angebot muss mindestens eine Position enthalten."
        )

    if len(items) > 3:
        raise QuotationError(
            reason="too_many_items",
            message="Ein Angebot darf höchstens 3 Positionen enthalten."
        )

    goods_net_cents = 0
    shipping_cents = 0
    lines = []
    seen_skus: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            raise QuotationError(
                reason="invalid_item_format",
                message="Jede Position muss ein Dictionary sein."
            )

        if "sku" not in item:
            raise QuotationError(
                reason="missing_sku",
                message="Position enthält keine SKU."
            )

        if "quantity" not in item:
            raise QuotationError(
                reason="missing_quantity",
                message="Position enthält keine Mengen-Angabe."
            )

        sku = item["sku"]
        quantity = item["quantity"]

        if sku in seen_skus:
            raise QuotationError(
                reason="duplicate_sku",
                message=f"Doppelte SKU '{sku}' im Angebot nicht zulässig."
            )
        seen_skus.add(sku)

        # Validierung: Menge darf kein bool sein
        if isinstance(quantity, bool):
            raise QuotationError(
                reason="quantity_wrong_type",
                message=f"Menge für {sku} ist kein gültiger Typ (bool)."
            )

        # Validierung: Menge darf keine Dezimalzahl/Bruchmenge sein
        if isinstance(quantity, float):
            raise QuotationError(
                reason="quantity_not_integer",
                message=f"Menge für {sku} darf keine Dezimalzahl/Bruchmenge sein."
            )

        if not isinstance(quantity, int):
            raise QuotationError(
                reason="quantity_wrong_type",
                message=f"Menge für {sku} muss eine ganze Zahl sein."
            )

        # Validierung: Menge im Bereich 1-10.000
        if quantity < 1 or quantity > 10000:
            raise QuotationError(
                reason="quantity_out_of_range",
                message=f"Menge für {sku} ({quantity}) liegt außerhalb des erlaubten Bereichs (1-10000)."
            )

        # Produkt im Katalog finden
        if sku not in catalog:
            raise QuotationError(
                reason="unknown_sku",
                message=f"SKU '{sku}' existiert nicht im Katalog."
            )

        product = catalog[sku]
        unit_price_cents = product.get("unit_price_cents", 0)

        # Listenbetrag berechnen
        list_amount_cents = quantity * unit_price_cents

        # Rabattberechnung nach HP-V1 Regeln
        if 1 <= quantity <= 50:
            discount_percent = 0
        elif 51 <= quantity <= 99:
            discount_percent = 5
        else:  # >= 100
            discount_percent = 10

        # Rabattbetrag berechnen (ROUND_HALF_UP nach Kundenbriefing: (Listenbetrag * Rabattsatz + 50) // 100)
        discount_cents = (list_amount_cents * discount_percent + 50) // 100

        # Netto berechnen
        net_cents = list_amount_cents - discount_cents
        goods_net_cents += net_cents

        lines.append({
            "sku": sku,
            "quantity": quantity,
            "unit_price_cents": unit_price_cents,
            "list_amount_cents": list_amount_cents,
            "discount_percent": discount_percent,
            "discount_cents": discount_cents,
            "net_cents": net_cents
        })
    
    # Versandberechnung nach HP-V1 Regeln
    if goods_net_cents < 50000:
        shipping_cents = 1200
    else:
        shipping_cents = 0
    
    total_cents = goods_net_cents + shipping_cents
    
    return {
        "lines": lines,
        "goods_net_cents": goods_net_cents,
        "shipping_cents": shipping_cents,
        "total_cents": total_cents,
        "currency": "EUR",
        "rule_version": rule_version
    }


def build_export_payload(quote: dict) -> dict:
    """
    Erstellt ein konsistentes Export-Payload aus einem berechneten Angebot.
    
    Validiert, dass alle Pflichtfelder vorhanden sind und Geldwerte ganzzahlige Cent-Werte sind.
    
    Args:
        quote: Das berechnete Angebots-Dictionary.
    
    Returns:
        Ein validiertes Dictionary für den Export.
    
    Raises:
        QuotationError: Wenn das Angebot ungültig ist (fehlende Felder oder falsche Typen).
    """
    required_fields = ["lines", "goods_net_cents", "shipping_cents", "total_cents", "currency", "rule_version"]
    
    # Prüfen, ob alle Pflichtfelder vorhanden sind
    for field in required_fields:
        if field not in quote:
            raise QuotationError(
                reason=f"missing_field",
                message=f"Fehlendes Pflichtfeld: {field}"
            )
    
    # Prüfen, ob Geldwerte ganzzahlige Cent-Werte sind (bool ist Unterklasse von int, muss explizit ausgeschlossen werden)
    monetary_fields = ["goods_net_cents", "shipping_cents", "total_cents"]
    for field in monetary_fields:
        value = quote[field]
        if not isinstance(value, int) or isinstance(value, bool):
            raise QuotationError(
                reason="invalid_monetary_type",
                message=f"Feld '{field}' muss ein ganzzahliges Integer-Wert sein (keine Floats oder Booleans)."
            )
    
    # currency und rule_version sollten Strings sein
    if not isinstance(quote["currency"], str):
        raise QuotationError(
            reason="invalid_currency_type",
            message=f"Feld 'currency' muss ein String sein."
        )
    
    if quote["rule_version"] != "HP-V1":
        raise QuotationError(
            reason="invalid_rule_version_in_payload",
            message=f"Im Export-Payload ist nur die Regelversion 'HP-V1' erlaubt (aktuell: {quote['rule_version']})."
        )
    
    # lines muss eine Liste von Dicts sein
    if not isinstance(quote["lines"], list):
        raise QuotationError(
            reason="invalid_lines_type",
            message=f"Feld 'lines' muss eine Liste sein."
        )
    
    return quote


def export_quote_json(quote: dict) -> str:
    """
    Serialisiert ein berechnetes Angebot als deterministisches JSON.
    
    Args:
        quote: Das berechnete Angebots-Dictionary (wird intern validiert).
    
    Returns:
        Eine JSON-String-Repräsentation des Angebots.
    
    Raises:
        QuotationError: Wenn das Angebot ungültig ist.
    """
    payload = build_export_payload(quote)
    return json.dumps(payload, indent=2, ensure_ascii=False)


def main():
    """CLI-Schnittstelle."""
    if len(sys.argv) != 3:
        print("Verwendung: python quotation.py <SKU> <Menge>", file=sys.stderr)
        sys.exit(1)
    
    sku = sys.argv[1]
    try:
        quantity = int(sys.argv[2])
    except ValueError:
        print(f"Fehler: Menge '{sys.argv[2]}' ist keine ganze Zahl.", file=sys.stderr)
        sys.exit(1)
    
    # Testfall: Nur einen Artikel pro Aufruf für einfache CLI-Tests
    items = [{"sku": sku, "quantity": quantity}]
    
    try:
        quote = calculate_quote(items)
        # Nutzung von export_quote_json für konsistente Ausgabe
        print(export_quote_json(quote))
    except QuotationError as e:
        print(f"Fehler: {e.message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
