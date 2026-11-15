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
    
    goods_net_cents = 0
    shipping_cents = 0
    lines = []
    
    for item in items:
        # Validierung: 'sku' und 'quantity' müssen vorhanden sein
        if "sku" not in item or "quantity" not in item:
            raise QuotationError(
                reason="missing_fields",
                message="Jeder Artikel muss 'sku' und 'quantity' enthalten."
            )
        
        sku = item["sku"]
        quantity = item["quantity"]
        
        # Validierung: Menge muss eine ganze Zahl sein (bool ist ungültig)
        if isinstance(quantity, bool):
            raise QuotationError(
                reason="invalid_quantity_type",
                message=f"Menge für {sku} ist kein gültiger Typ (bool)."
            )
        
        if not isinstance(quantity, int):
            raise QuotationError(
                reason="invalid_quantity_type",
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
                reason="sku_not_found",
                message=f"SKU '{sku}' existiert nicht im Katalog."
            )
        
        product = catalog[sku]
        unit_price_cents = product.get("unit_price_cents", 0)
        
        # Listenbetrag berechnen
        list_amount_cents = quantity * unit_price_cents
        
        # Rabattberechnung nach HP-V1 Regeln
        if 1 <= quantity <= 49:
            discount_percent = 0
        elif 50 <= quantity <= 99:
            discount_percent = 5
        else:  # >= 100
            discount_percent = 10
        
        # Rabattbetrag berechnen (ROUND_HALF_UP)
        discount_cents = int((Decimal(list_amount_cents) * Decimal(discount_percent)) / Decimal(100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        
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
        print(json.dumps(quote, indent=2, ensure_ascii=False))
    except QuotationError as e:
        print(f"Fehler: {e.message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
