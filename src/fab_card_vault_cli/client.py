from __future__ import annotations

import os
from collections.abc import Mapping

import httpx

from fab_card_vault_cli.errors import InvalidPageError, NotFoundError, UpstreamError
from fab_card_vault_cli.mappers import (
    as_mapping,
    map_card_detail,
    map_card_prints,
    map_product_groups,
    map_search_results,
)
from fab_card_vault_cli.models import Card, CardDetail, CardPrint, ProductGroupsPage

DEFAULT_API_BASE = "https://api.cardvault.fabtcg.com/carddb/api/v1"
DEFAULT_TIMEOUT_SECONDS = 15.0


class CardVaultClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = (
            base_url or os.environ.get("FAB_CARD_VAULT_API_BASE") or DEFAULT_API_BASE
        ).rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=httpx.Timeout(timeout_seconds),
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def search(self, query: str) -> list[Card]:
        payload = self._get_json(
            "advanced-search/",
            params={"q": query, "page_size": 60, "orderby": "name"},
        )
        return map_search_results(payload)

    def get_prints(self, card_id: str) -> list[CardPrint]:
        payload = self._get_json(f"card_id/{card_id}/")
        if not payload.get("results"):
            raise NotFoundError(
                f"cardId='{card_id}' に一致するカードが見つかりませんでした",
                {"cardId": card_id},
            )
        return map_card_prints(card_id, payload)

    def get_detail(self, card_id: str, print_id: str | None = None) -> CardDetail:
        payload = self._get_json(f"card_id/{card_id}/")
        if not payload.get("results"):
            raise NotFoundError(
                f"cardId='{card_id}' に一致するカードが見つかりませんでした",
                {"cardId": card_id},
            )

        try:
            return map_card_detail(card_id, payload, print_id)
        except LookupError as exc:
            raise NotFoundError(str(exc), {"cardId": card_id}) from exc
        except KeyError as exc:
            raise NotFoundError(
                str(exc).strip("'"),
                {"cardId": card_id, "printId": print_id},
            ) from exc
        except ValueError as exc:
            raise NotFoundError(str(exc), {"cardId": card_id}) from exc

    def get_products(self, page: int = 1) -> ProductGroupsPage:
        response = self._request("product-groups-products/", params={"page": page})
        if response.status_code == 404:
            raise InvalidPageError(
                f"page={page} は無効です。別のページ番号を指定してください。",
                {"page": page},
            )
        self._raise_for_status(response, "product-groups-products/")
        payload = self._decode_json(response, "product-groups-products/")
        return map_product_groups(page, payload)

    def _get_json(
        self,
        path: str,
        params: Mapping[str, str | int] | None = None,
    ) -> Mapping[str, object]:
        response = self._request(path, params=params)
        self._raise_for_status(response, path)
        return self._decode_json(response, path)

    def _request(
        self,
        path: str,
        params: Mapping[str, str | int] | None = None,
    ) -> httpx.Response:
        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            return self._client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise UpstreamError(
                "CardVault API request timed out.",
                {"path": path},
            ) from exc
        except httpx.RequestError as exc:
            raise UpstreamError(
                "Failed to reach the CardVault API.",
                {"path": path, "reason": str(exc)},
            ) from exc

    def _raise_for_status(self, response: httpx.Response, path: str) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise UpstreamError(
                f"CardVault API returned HTTP {response.status_code}.",
                {"path": path, "statusCode": response.status_code},
            ) from exc

    def _decode_json(self, response: httpx.Response, path: str) -> Mapping[str, object]:
        try:
            return as_mapping(response.json())
        except ValueError as exc:
            raise UpstreamError(
                "CardVault API returned invalid JSON.",
                {"path": path},
            ) from exc
