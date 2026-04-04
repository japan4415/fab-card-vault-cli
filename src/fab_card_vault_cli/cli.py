from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Literal, NoReturn

import typer
from rich.console import Console

from fab_card_vault_cli.client import CardVaultClient
from fab_card_vault_cli.errors import FabCardVaultError, NotFoundError
from fab_card_vault_cli.output import emit_error, emit_payload
from fab_card_vault_cli.rulings import search_rulings

OutputFormat = Literal["json", "pretty"]

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
    help="Flesh and Blood CardVault JSON-first CLI",
)


@dataclass(slots=True)
class AppState:
    output_format: OutputFormat
    client: CardVaultClient
    stdout: Console
    stderr: Console

    def close(self) -> None:
        self.client.close()


def get_state(ctx: typer.Context) -> AppState:
    state = ctx.obj
    if not isinstance(state, AppState):
        raise RuntimeError("CLI state has not been initialized.")
    return state


def handle_error(state: AppState, error: FabCardVaultError) -> NoReturn:
    emit_error(state.stderr, error, state.output_format)
    raise typer.Exit(code=1)


@app.callback()
def main_callback(
    ctx: typer.Context,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            help="Output format.",
            case_sensitive=False,
        ),
    ] = "json",
) -> None:
    state = AppState(
        output_format=output_format,
        client=CardVaultClient(),
        stdout=Console(stderr=False),
        stderr=Console(stderr=True),
    )
    ctx.obj = state
    ctx.call_on_close(state.close)


@app.command("search")
def search_command(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Card name, type, or text query.")],
) -> None:
    state = get_state(ctx)
    try:
        emit_payload(state.stdout, state.client.search(query), state.output_format)
    except FabCardVaultError as error:
        handle_error(state, error)


@app.command("prints")
def prints_command(
    ctx: typer.Context,
    card_id: Annotated[str, typer.Argument(help="Card identifier returned by search.")],
) -> None:
    state = get_state(ctx)
    try:
        emit_payload(state.stdout, state.client.get_prints(card_id), state.output_format)
    except FabCardVaultError as error:
        handle_error(state, error)


@app.command("detail")
def detail_command(
    ctx: typer.Context,
    card_id: Annotated[str, typer.Argument(help="Card identifier returned by search.")],
    print_id: Annotated[
        str | None,
        typer.Option("--print-id", help="Specific print or face identifier."),
    ] = None,
) -> None:
    state = get_state(ctx)
    try:
        detail = state.client.get_detail(card_id, print_id)
        matched = search_rulings(detail.enName)
        if matched:
            exact = [r for r in matched if r.cardName.lower() == detail.enName.lower()]
            if exact:
                detail.rulings = [note for r in exact for note in r.notes]
        emit_payload(state.stdout, detail, state.output_format)
    except FabCardVaultError as error:
        handle_error(state, error)


@app.command("products")
def products_command(
    ctx: typer.Context,
    page: Annotated[
        int,
        typer.Option("--page", min=1, help="Product page number."),
    ] = 1,
) -> None:
    state = get_state(ctx)
    try:
        emit_payload(state.stdout, state.client.get_products(page), state.output_format)
    except FabCardVaultError as error:
        handle_error(state, error)


@app.command("rulings")
def rulings_command(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Card name to search rulings for.")],
) -> None:
    state = get_state(ctx)
    results = search_rulings(query)
    if not results:
        handle_error(state, NotFoundError(f"No rulings found for '{query}'.", {"query": query}))
    emit_payload(state.stdout, results, state.output_format)


def main() -> None:
    app()
