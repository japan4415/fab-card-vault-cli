from __future__ import annotations

from fab_card_vault_cli.models import Ruling
from fab_card_vault_cli.rulings import load_rulings, search_rulings


def test_load_rulings_returns_list_of_ruling_objects() -> None:
    result = load_rulings()

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(r, Ruling) for r in result)
    assert all(r.cardName for r in result)
    assert all(isinstance(r.notes, list) for r in result)


def test_search_rulings_partial_match() -> None:
    results = search_rulings("Absorb")

    assert len(results) > 0
    assert any("Absorb" in r.cardName for r in results)


def test_search_rulings_case_insensitive() -> None:
    upper = search_rulings("ABSORB")
    lower = search_rulings("absorb")

    assert len(upper) > 0
    assert upper == lower


def test_search_rulings_no_match() -> None:
    results = search_rulings("ZZZZNONEXISTENTCARD")

    assert results == []
