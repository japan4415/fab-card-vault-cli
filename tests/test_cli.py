from __future__ import annotations

import json

from typer.testing import CliRunner

from fab_card_vault_cli.cli import app

runner = CliRunner()


def test_search_returns_expected_json(httpx_mock) -> None:
    httpx_mock.add_response(
        url=(
            "https://api.cardvault.fabtcg.com/carddb/api/v1/advanced-search/"
            "?q=Awakening&page_size=60&orderby=name"
        ),
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "card_id": "awakening-3",
                    "print_id": "U-ELE006",
                    "printed_name": "Awakening",
                    "printed_pitch": 3,
                    "printed_cost": "2",
                    "printed_power": "",
                    "printed_defense": "",
                    "printed_rules_text": "Search your deck.",
                    "printed_typebox": "Elemental Guardian Instant",
                    "faces": [
                        {
                            "layout_position": 10,
                            "image": {
                                "small": "https://example.com/small.webp",
                                "normal": "https://example.com/normal.webp",
                                "large": "https://example.com/large.webp",
                            },
                        }
                    ],
                }
            ],
        },
    )

    result = runner.invoke(app, ["search", "Awakening"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload == [
        {
            "id": "awakening-3",
            "name": "Awakening",
            "displayName": "Awakening",
            "cardUrl": "https://cardvault.fabtcg.com/card/awakening-3/U-ELE006",
            "imageUrl": "https://example.com/normal.webp",
            "pitch": "3",
            "cost": "2",
            "text": "Search your deck.",
            "typebox": "Elemental Guardian Instant",
        }
    ]


def test_prints_returns_mcp_compatible_shape(httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.cardvault.fabtcg.com/carddb/api/v1/card_id/awakening-3/",
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "card_id": "awakening-3",
                    "card_prints": [
                        {
                            "print_id": "U-ELE006",
                            "layout": "regular",
                            "faces": [
                                {
                                    "face_id": "U-ELE006",
                                    "finish_type": "regular",
                                    "printed_name": "Awakening",
                                    "printed_pitch": 3,
                                    "layout_position": 10,
                                    "image": {
                                        "small": "https://example.com/small.webp",
                                        "normal": "https://example.com/normal.webp",
                                        "large": "https://example.com/large.webp",
                                    },
                                },
                                {
                                    "face_id": "U-ELE006-RF",
                                    "finish_type": "rainbow-foil",
                                    "layout_position": 20,
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    )

    result = runner.invoke(app, ["prints", "awakening-3"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload == [
        {
            "printId": "U-ELE006",
            "cardId": "awakening-3",
            "name": "Awakening",
            "displayName": "Awakening",
            "pitch": "3",
            "imageUrl": "https://example.com/normal.webp",
            "imageUrlSmall": "https://example.com/small.webp",
            "imageUrlLarge": "https://example.com/large.webp",
            "layout": {"key": "regular", "label": "Regular"},
            "finishTypes": [
                {"key": "rainbow-foil", "label": "Rainbow Foil"},
                {"key": "regular", "label": "Regular"},
            ],
        }
    ]


def test_detail_with_print_id_returns_language_fields(httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.cardvault.fabtcg.com/carddb/api/v1/card_id/awakening-3/",
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "card_id": "awakening-3",
                    "cores": [{"pitch": "3", "cost": "2", "power": "", "defense": ""}],
                    "card_prints": [
                        {
                            "print_id": "U-ELE006",
                            "print_language": "en",
                            "rarity": "majestic",
                            "layout": "regular",
                            "product": {"product_name": "Tales of Aria - Unlimited"},
                            "print_set": {"set_name": "Tales of Aria"},
                            "faces": [
                                {
                                    "face_id": "U-ELE006",
                                    "face_language": "en",
                                    "finish_type": "regular",
                                    "printed_name": "Awakening",
                                    "printed_rules_text": "English text",
                                    "printed_typebox": "Elemental Guardian Instant",
                                    "printed_artist": "Nathaniel Himawan",
                                    "printed_pitch": 3,
                                    "printed_cost": "2",
                                    "layout_position": 10,
                                    "image": {"normal": "https://example.com/en.webp"},
                                }
                            ],
                        },
                        {
                            "print_id": "JA_GAP008",
                            "print_language": "ja",
                            "rarity": "majestic",
                            "layout": "regular",
                            "product": {"product_name": "Mastery Pack Archive - Guardian [JA]"},
                            "print_set": {"set_name": "Mastery Pack Archive - Guardian"},
                            "faces": [
                                {
                                    "face_id": "JA_GAP008",
                                    "face_language": "ja",
                                    "finish_type": "regular",
                                    "printed_name": "覚醒",
                                    "printed_rules_text": "日本語テキスト",
                                    "printed_typebox": "エレメンタル・守護者・インスタント",
                                    "printed_artist": "Nathaniel Himawan",
                                    "printed_pitch": 3,
                                    "printed_cost": "2",
                                    "layout_position": 10,
                                    "image": {"normal": "https://example.com/ja.webp"},
                                }
                            ],
                        },
                    ],
                }
            ],
        },
    )

    result = runner.invoke(app, ["detail", "awakening-3", "--print-id", "JA_GAP008"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["cardId"] == "awakening-3"
    assert payload["printId"] == "JA_GAP008"
    assert payload["enName"] == "Awakening"
    assert payload["jaName"] == "覚醒"
    assert payload["jaText"] == "日本語テキスト"
    assert payload["variants"][0]["url"].startswith("https://cardvault.fabtcg.com/card/")


def test_detail_without_print_id_uses_default_print(httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.cardvault.fabtcg.com/carddb/api/v1/card_id/awakening-3/",
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "card_id": "awakening-3",
                    "cores": [{"pitch": "3", "cost": "2"}],
                    "card_prints": [
                        {
                            "print_id": "ELE006",
                            "is_default": True,
                            "rarity": "majestic",
                            "product": {"product_name": "Tales of Aria"},
                            "print_set": {"set_name": "Tales of Aria"},
                            "faces": [
                                {
                                    "face_id": "ELE006",
                                    "face_language": "en",
                                    "printed_name": "Awakening",
                                    "printed_rules_text": "English text",
                                    "printed_typebox": "Elemental Guardian Instant",
                                    "printed_pitch": 3,
                                    "printed_cost": "2",
                                    "layout_position": 10,
                                    "image": {"normal": "https://example.com/default.webp"},
                                }
                            ],
                        }
                    ],
                }
            ],
        },
    )

    result = runner.invoke(app, ["detail", "awakening-3"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["printId"] == "ELE006"
    assert payload["imageUrl"] == "https://example.com/default.webp"


def test_products_returns_pagination_fields(httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.cardvault.fabtcg.com/carddb/api/v1/product-groups-products/?page=1",
        json={
            "count": 107,
            "next": "https://api.cardvault.fabtcg.com/carddb/api/v1/product-groups-products/?page=2",
            "previous": None,
            "results": [
                {
                    "id": "group-1",
                    "group_name": "Silver Age Chapter 3 - Boltyn",
                    "product_type": "precon",
                    "release_date": "2026-06-05",
                    "products": [
                        {
                            "id": "prod-1",
                            "product_name": "Silver Age Chapter 3 - Boltyn",
                            "printed_language": "en",
                            "printed_date": "2025-12-24",
                            "product_type": "precon",
                            "release_date": "2026-06-05",
                            "slug": "silver-age-chapter-3-boltyn",
                            "description": "",
                        }
                    ],
                }
            ],
        },
    )

    result = runner.invoke(app, ["products", "--page", "1"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["page"] == 1
    assert payload["count"] == 107
    assert payload["nextPage"] == 2
    assert payload["productGroups"][0]["products"][0]["language"] == "EN"


def test_invalid_page_returns_json_error_on_stderr(httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.cardvault.fabtcg.com/carddb/api/v1/product-groups-products/?page=999",
        status_code=404,
        json={"detail": "Invalid page."},
    )

    result = runner.invoke(app, ["products", "--page", "999"])

    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["error"]["type"] == "invalid_page"
    assert payload["error"]["details"]["page"] == 999


def test_rulings_command_returns_matching_results(monkeypatch) -> None:
    from fab_card_vault_cli import cli as cli_mod
    from fab_card_vault_cli.models import Ruling

    fake = [Ruling(cardName="Awakening", setName="Arcane Rising", notes=["Note A", "Note B"])]
    monkeypatch.setattr(cli_mod, "search_rulings", lambda _q: fake)

    result = runner.invoke(app, ["rulings", "Awakening"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
    assert payload[0]["cardName"] == "Awakening"
    assert payload[0]["notes"] == ["Note A", "Note B"]


def test_rulings_command_not_found_returns_error(monkeypatch) -> None:
    from fab_card_vault_cli import cli as cli_mod

    monkeypatch.setattr(cli_mod, "search_rulings", lambda _q: [])

    result = runner.invoke(app, ["rulings", "NonExistentCard"])

    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["error"]["type"] == "not_found"


def test_detail_includes_rulings_when_available(httpx_mock, monkeypatch) -> None:
    from fab_card_vault_cli import cli as cli_mod
    from fab_card_vault_cli.models import Ruling

    httpx_mock.add_response(
        url="https://api.cardvault.fabtcg.com/carddb/api/v1/card_id/awakening-3/",
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "card_id": "awakening-3",
                    "cores": [{"pitch": "3", "cost": "2"}],
                    "card_prints": [
                        {
                            "print_id": "ELE006",
                            "is_default": True,
                            "rarity": "majestic",
                            "product": {"product_name": "Tales of Aria"},
                            "print_set": {"set_name": "Tales of Aria"},
                            "faces": [
                                {
                                    "face_id": "ELE006",
                                    "face_language": "en",
                                    "printed_name": "Awakening",
                                    "printed_rules_text": "English text",
                                    "printed_typebox": "Elemental Guardian Instant",
                                    "printed_pitch": 3,
                                    "printed_cost": "2",
                                    "layout_position": 10,
                                    "image": {"normal": "https://example.com/default.webp"},
                                }
                            ],
                        }
                    ],
                }
            ],
        },
    )

    fake = [Ruling(cardName="Awakening", setName="Arcane Rising", notes=["Ruling 1", "Ruling 2"])]
    monkeypatch.setattr(cli_mod, "search_rulings", lambda _q: fake)

    result = runner.invoke(app, ["detail", "awakening-3"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["rulings"] == ["Ruling 1", "Ruling 2"]


def test_pretty_output_uses_human_readable_rendering(httpx_mock) -> None:
    httpx_mock.add_response(
        url=(
            "https://api.cardvault.fabtcg.com/carddb/api/v1/advanced-search/"
            "?q=Awakening&page_size=60&orderby=name"
        ),
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "card_id": "awakening-3",
                    "print_id": "U-ELE006",
                    "printed_name": "Awakening",
                    "faces": [{"image": {"normal": "https://example.com/normal.webp"}}],
                }
            ],
        },
    )

    result = runner.invoke(app, ["--format", "pretty", "search", "Awakening"])

    assert result.exit_code == 0
    assert "Awakening" in result.stdout
    assert "cardUrl" in result.stdout
