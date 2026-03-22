from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from fab_card_vault_cli.models import (
    Card,
    CardDetail,
    CardPrint,
    FinishType,
    Layout,
    ProductGroupsPage,
    ProductGroupSummary,
    ProductSummary,
    Variant,
)

CARDVAULT_WEB_BASE = "https://cardvault.fabtcg.com"


def as_optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def as_string_or_empty(value: object) -> str:
    return as_optional_string(value) or ""


def as_mapping(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return cast(Mapping[str, object], value)
    return {}


def as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return cast(list[object], value)
    return []


def get_faces(raw_faces: object) -> list[Mapping[str, object]]:
    return [as_mapping(face) for face in as_list(raw_faces)]


def get_image(face: Mapping[str, object]) -> Mapping[str, object]:
    return as_mapping(face.get("image"))


def format_label(value: str) -> str:
    words = [word for word in value.replace("-", " ").replace("_", " ").split() if word]
    return " ".join(word[:1].upper() + word[1:] for word in words)


def normalize_language_code(code: object) -> str:
    return (as_optional_string(code) or "en").upper()


def pick_primary_face(
    faces: list[Mapping[str, object]],
    preferred_face_id: str | None = None,
) -> Mapping[str, object] | None:
    if preferred_face_id:
        for face in faces:
            if as_optional_string(face.get("face_id")) == preferred_face_id:
                return face

    if not faces:
        return None

    return min(
        faces,
        key=lambda face: (
            face.get("layout_position")
            if isinstance(face.get("layout_position"), int)
            else 2**31 - 1
        ),
    )


def find_face_by_language(
    card_prints: list[Mapping[str, object]],
    language_code: str,
) -> Mapping[str, object] | None:
    normalized_language_code = language_code.lower()
    for card_print in card_prints:
        for face in get_faces(card_print.get("faces")):
            face_language = as_optional_string(face.get("face_language"))
            if face_language and face_language.lower() == normalized_language_code:
                return face
    return None


def build_variants(card_id: str, card_prints: list[Mapping[str, object]]) -> list[Variant]:
    variants: dict[str, Variant] = {}

    for card_print in card_prints:
        faces = get_faces(card_print.get("faces"))
        for face in faces:
            variant_print_id = as_optional_string(face.get("face_id")) or as_optional_string(
                card_print.get("print_id")
            )
            if not variant_print_id or variant_print_id in variants:
                continue

            product = as_mapping(card_print.get("product"))
            print_set = as_mapping(card_print.get("print_set"))
            set_name = (
                as_optional_string(product.get("product_name"))
                or as_optional_string(print_set.get("set_name"))
                or ""
            )
            finish_type = as_optional_string(face.get("finish_type")) or "regular"

            variants[variant_print_id] = Variant(
                printId=variant_print_id,
                language=normalize_language_code(
                    face.get("face_language") or card_print.get("print_language")
                ),
                setName=set_name,
                finishType=finish_type,
                url=f"{CARDVAULT_WEB_BASE}/card/{card_id}/{variant_print_id}",
            )

    return list(variants.values())


def parse_page_number_from_url(url_text: object) -> int | None:
    resolved_url_text = as_optional_string(url_text)
    if not resolved_url_text:
        return None

    from urllib.parse import parse_qs, urlparse

    query = parse_qs(urlparse(resolved_url_text).query)
    page_values = query.get("page")
    if not page_values:
        return None

    page_text = as_optional_string(page_values[0])
    if page_text is None:
        return None

    try:
        page = int(page_text)
    except ValueError:
        return None

    return page if page > 0 else None


def map_search_results(payload: Mapping[str, object]) -> list[Card]:
    cards: list[Card] = []
    for raw_card in as_list(payload.get("results")):
        card = as_mapping(raw_card)
        primary_face = pick_primary_face(get_faces(card.get("faces")))
        primary_image = get_image(primary_face or {})
        card_id = as_string_or_empty(card.get("card_id"))
        print_id = as_string_or_empty(card.get("print_id"))
        name = as_optional_string(card.get("printed_name")) or card_id

        cards.append(
            Card(
                id=card_id,
                name=name,
                displayName=name,
                cardUrl=f"{CARDVAULT_WEB_BASE}/card/{card_id}/{print_id}",
                imageUrl=as_string_or_empty(primary_image.get("normal")),
                pitch=as_optional_string(card.get("printed_pitch")),
                cost=as_optional_string(card.get("printed_cost")),
                power=as_optional_string(card.get("printed_power")),
                defense=as_optional_string(card.get("printed_defense")),
                text=as_optional_string(card.get("printed_rules_text")),
                typebox=as_optional_string(card.get("printed_typebox")),
            )
        )

    return cards


def map_card_prints(card_id: str, payload: Mapping[str, object]) -> list[CardPrint]:
    card = first_result(payload)
    if not card:
        return []

    prints: list[CardPrint] = []
    for raw_card_print in as_list(card.get("card_prints")):
        card_print = as_mapping(raw_card_print)
        print_id = as_optional_string(card_print.get("print_id"))
        if print_id is None:
            continue

        faces = get_faces(card_print.get("faces"))
        primary_face = pick_primary_face(faces)
        primary_image = get_image(primary_face or {})
        finish_keys = sorted(
            {
                finish_type
                for finish_type in (as_optional_string(face.get("finish_type")) for face in faces)
                if finish_type
            }
        )
        name = as_optional_string((primary_face or {}).get("printed_name")) or print_id or card_id

        prints.append(
            CardPrint(
                printId=print_id,
                cardId=card_id,
                name=name,
                displayName=name,
                pitch=as_optional_string((primary_face or {}).get("printed_pitch")),
                imageUrl=as_string_or_empty(primary_image.get("normal")),
                imageUrlSmall=as_string_or_empty(primary_image.get("small")),
                imageUrlLarge=as_string_or_empty(primary_image.get("large")),
                layout=Layout(
                    key=as_optional_string(card_print.get("layout")) or "unknown",
                    label=format_label(as_optional_string(card_print.get("layout")) or "unknown"),
                ),
                finishTypes=[
                    FinishType(key=finish_key, label=format_label(finish_key))
                    for finish_key in finish_keys
                ],
            )
        )

    return prints


def first_result(payload: Mapping[str, object]) -> Mapping[str, object] | None:
    results = as_list(payload.get("results"))
    if not results:
        return None
    return as_mapping(results[0])


def map_card_detail(
    card_id: str, payload: Mapping[str, object], print_id: str | None
) -> CardDetail:
    card = first_result(payload)
    if not card:
        raise ValueError(f"cardId='{card_id}' に一致するカードが見つかりませんでした")

    resolved_card_id = as_optional_string(card.get("card_id")) or card_id
    card_prints = [as_mapping(item) for item in as_list(card.get("card_prints"))]
    if not card_prints:
        raise LookupError(f"cardId='{resolved_card_id}' に利用可能なカードプリントがありません")

    selected_print: Mapping[str, object] | None = None
    preferred_face_id: str | None = None

    if print_id:
        for candidate in card_prints:
            if as_optional_string(candidate.get("print_id")) == print_id:
                selected_print = candidate
                break
        if selected_print is None:
            for candidate in card_prints:
                faces = get_faces(candidate.get("faces"))
                if any(as_optional_string(face.get("face_id")) == print_id for face in faces):
                    selected_print = candidate
                    preferred_face_id = print_id
                    break
        if selected_print is None:
            raise KeyError(f"cardId='{resolved_card_id}' に printId='{print_id}' は存在しません")
    else:
        selected_print = next(
            (
                candidate
                for candidate in card_prints
                if isinstance(candidate.get("is_default"), bool) and candidate.get("is_default")
            ),
            None,
        )
        if selected_print is None:
            selected_print = card_prints[0]

    selected_faces = get_faces(selected_print.get("faces"))
    selected_face = pick_primary_face(selected_faces, preferred_face_id or print_id)
    english_face = find_face_by_language(card_prints, "en")
    japanese_face = find_face_by_language(card_prints, "ja")
    selected_image = get_image(selected_face or {})
    product = as_mapping(selected_print.get("product"))
    print_set = as_mapping(selected_print.get("print_set"))
    cores = [as_mapping(core) for core in as_list(card.get("cores"))]
    primary_core = cores[0] if cores else {}

    resolved_print_id = (
        as_optional_string((selected_face or {}).get("face_id"))
        or as_optional_string(selected_print.get("print_id"))
        or print_id
        or ""
    )

    return CardDetail(
        cardId=resolved_card_id,
        printId=resolved_print_id,
        imageUrl=as_string_or_empty(selected_image.get("normal")),
        enName=(
            as_optional_string((english_face or {}).get("printed_name"))
            or as_optional_string((selected_face or {}).get("printed_name"))
            or resolved_card_id
        ),
        enText=(
            as_optional_string((english_face or {}).get("printed_rules_text"))
            or as_optional_string((selected_face or {}).get("printed_rules_text"))
        ),
        enTypebox=(
            as_optional_string((english_face or {}).get("printed_typebox"))
            or as_optional_string((selected_face or {}).get("printed_typebox"))
        ),
        jaName=as_optional_string((japanese_face or {}).get("printed_name")),
        jaText=as_optional_string((japanese_face or {}).get("printed_rules_text")),
        jaTypebox=as_optional_string((japanese_face or {}).get("printed_typebox")),
        pitch=(
            as_optional_string((selected_face or {}).get("printed_pitch"))
            or as_optional_string(primary_core.get("pitch"))
        ),
        cost=(
            as_optional_string((selected_face or {}).get("printed_cost"))
            or as_optional_string(primary_core.get("cost"))
        ),
        power=(
            as_optional_string((selected_face or {}).get("printed_power"))
            or as_optional_string(primary_core.get("power"))
        ),
        defense=(
            as_optional_string((selected_face or {}).get("printed_defense"))
            or as_optional_string(primary_core.get("defense"))
        ),
        set=(
            as_optional_string(print_set.get("set_name"))
            or as_optional_string(product.get("product_name"))
        ),
        rarity=as_optional_string(selected_print.get("rarity")),
        artist=as_optional_string((selected_face or {}).get("printed_artist")),
        variants=build_variants(resolved_card_id, card_prints),
    )


def map_product_groups(page: int, payload: Mapping[str, object]) -> ProductGroupsPage:
    groups: list[ProductGroupSummary] = []
    for raw_group in as_list(payload.get("results")):
        group = as_mapping(raw_group)
        products: list[ProductSummary] = []
        for raw_product in as_list(group.get("products")):
            product = as_mapping(raw_product)
            products.append(
                ProductSummary(
                    id=as_string_or_empty(product.get("id")),
                    productName=as_string_or_empty(product.get("product_name")),
                    slug=as_optional_string(product.get("slug")),
                    language=normalize_language_code(product.get("printed_language"))
                    if as_optional_string(product.get("printed_language"))
                    else None,
                    printedDate=as_optional_string(product.get("printed_date")),
                    productType=as_optional_string(product.get("product_type")),
                    releaseDate=as_optional_string(product.get("release_date")),
                    description=as_optional_string(product.get("description")),
                )
            )
        groups.append(
            ProductGroupSummary(
                id=as_string_or_empty(group.get("id")),
                groupName=as_string_or_empty(group.get("group_name")),
                productType=as_optional_string(group.get("product_type")),
                releaseDate=as_optional_string(group.get("release_date")),
                products=products,
            )
        )

    count_value = payload.get("count")
    count = count_value if isinstance(count_value, int) else 0

    return ProductGroupsPage(
        page=page,
        count=count,
        next=as_optional_string(payload.get("next")),
        previous=as_optional_string(payload.get("previous")),
        nextPage=parse_page_number_from_url(payload.get("next")),
        previousPage=parse_page_number_from_url(payload.get("previous")),
        productGroups=groups,
    )
