from __future__ import annotations

import json
from importlib.resources import files

from fab_card_vault_cli.models import Ruling


def load_rulings() -> list[Ruling]:
    """Load rulings from the bundled JSON file.

    Returns:
        List of Ruling dataclass instances.
    """
    data_path = files("fab_card_vault_cli").joinpath("data/rulings.json")
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    return [Ruling(cardName=r["card_name"], setName=r["set_name"], notes=r["notes"]) for r in raw]


def search_rulings(query: str) -> list[Ruling]:
    """Search rulings by card name (case-insensitive partial match).

    Args:
        query: Card name substring to search for.

    Returns:
        List of matching Ruling instances.
    """
    rulings = load_rulings()
    q = query.lower()
    return [r for r in rulings if q in r.cardName.lower()]
