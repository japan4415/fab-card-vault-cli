from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Card:
    id: str
    name: str
    displayName: str
    cardUrl: str
    imageUrl: str
    pitch: str | None = None
    cost: str | None = None
    power: str | None = None
    defense: str | None = None
    text: str | None = None
    typebox: str | None = None


@dataclass(slots=True)
class FinishType:
    key: str
    label: str


@dataclass(slots=True)
class Layout:
    key: str
    label: str


@dataclass(slots=True)
class CardPrint:
    printId: str
    cardId: str
    name: str
    displayName: str
    imageUrl: str
    imageUrlSmall: str
    imageUrlLarge: str
    layout: Layout
    finishTypes: list[FinishType]
    pitch: str | None = None


@dataclass(slots=True)
class Variant:
    printId: str
    language: str
    setName: str
    finishType: str
    url: str


@dataclass(slots=True)
class CardDetail:
    cardId: str
    printId: str
    imageUrl: str
    enName: str
    enText: str | None = None
    enTypebox: str | None = None
    jaName: str | None = None
    jaText: str | None = None
    jaTypebox: str | None = None
    pitch: str | None = None
    cost: str | None = None
    power: str | None = None
    defense: str | None = None
    set: str | None = None
    rarity: str | None = None
    artist: str | None = None
    variants: list[Variant] | None = None
    rulings: list[str] | None = None


@dataclass(slots=True)
class ProductSummary:
    id: str
    productName: str
    slug: str | None = None
    language: str | None = None
    printedDate: str | None = None
    productType: str | None = None
    releaseDate: str | None = None
    description: str | None = None


@dataclass(slots=True)
class ProductGroupSummary:
    id: str
    groupName: str
    products: list[ProductSummary]
    productType: str | None = None
    releaseDate: str | None = None


@dataclass(slots=True)
class Ruling:
    cardName: str
    setName: str
    notes: list[str]


@dataclass(slots=True)
class ProductGroupsPage:
    page: int
    count: int
    next: str | None
    previous: str | None
    nextPage: int | None
    previousPage: int | None
    productGroups: list[ProductGroupSummary]
