"""HansePack Angebotsrechner – Fachlogik (Starter, wird durch die Factory implementiert).

Spezifikation: issue_hp01.md
"""
from __future__ import annotations


class QuotationError(ValueError):
    """Ungültige Angebotseingabe. `reason` ist ein semantischer Fehlercode."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


def calculate_quote(items: list[dict], rule_version: str = "HP-V1") -> dict:
    raise NotImplementedError("TODO: implement according to issue_hp01.md")
