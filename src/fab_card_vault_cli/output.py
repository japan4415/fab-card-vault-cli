from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from typing import cast

from rich.console import Console
from rich.json import JSON

from fab_card_vault_cli.errors import FabCardVaultError

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def to_jsonable(value: object) -> JsonValue:
    if is_dataclass(value):
        data: dict[str, JsonValue] = {}
        for field in fields(value):
            raw_value = getattr(value, field.name)
            if raw_value is None:
                continue
            data[field.name] = to_jsonable(raw_value)
        return data

    if isinstance(value, dict):
        data: dict[str, JsonValue] = {}
        for key, item in value.items():
            if item is None:
                continue
            data[str(key)] = to_jsonable(item)
        return data

    if isinstance(value, list | tuple):
        return [to_jsonable(item) for item in value]

    if isinstance(value, str | int | float | bool) or value is None:
        return cast(JsonValue, value)

    return str(value)


def emit_payload(console: Console, payload: object, output_format: str) -> None:
    jsonable = to_jsonable(payload)
    if output_format == "pretty":
        console.print(JSON.from_data(jsonable))
        return

    console.print_json(data=jsonable)


def emit_error(console: Console, error: FabCardVaultError, output_format: str) -> None:
    if output_format == "pretty":
        console.print(f"[bold red]{error.message}[/bold red]")
        return

    console.print(json.dumps(to_jsonable(error.to_payload()), ensure_ascii=False, indent=2))
