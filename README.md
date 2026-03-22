# fab-card-vault-cli

`fab-card-vault-cli` is a JSON-first command-line interface for the Flesh and Blood CardVault API. It is designed for direct use from shells, scripts, and AI agents without any long-running background service.

The CLI provides four core workflows:

- Search cards by name or text
- List print variants for a card
- Fetch detailed card data, including language variants
- Browse product groups with pagination

## Setup

```bash
uv sync --dev
```

To install it as a global tool:

```bash
uv tool install .
```

To run it from the repository:

```bash
uv run fab-card-vault --help
```

## Quick Start

Search for cards:

```bash
uv run fab-card-vault search Awakening
```

List print variants for a card:

```bash
uv run fab-card-vault prints awakening-3
```

Get detailed card data:

```bash
uv run fab-card-vault detail awakening-3 --print-id JA_GAP008
```

Browse product groups:

```bash
uv run fab-card-vault products --page 1
```

## Output Model

The default output format is JSON on standard output. This makes the CLI easy to pipe into tools such as `jq`, shell scripts, or agent workflows.

Use `--format pretty` when you want human-friendly, colorized output instead:

```bash
uv run fab-card-vault --format pretty search Awakening
```

## jq Examples

Extract the first card ID:

```bash
uv run fab-card-vault search Awakening | jq -r '.[0].id'
```

Find Japanese print IDs:

```bash
uv run fab-card-vault detail awakening-3 | jq -r '.variants[] | select(.language == "JA") | .printId'
```

List product names:

```bash
uv run fab-card-vault products --page 1 | jq -r '.productGroups[].products[].productName'
```

## Commands

`search <query>`

Searches CardVault and returns matching cards.

`prints <card_id>`

Returns the available print entries for a card ID.

`detail <card_id> [--print-id <print_id>]`

Returns detailed card data, including English and Japanese fields when available.

`products [--page <n>]`

Returns product groups and nested product entries for the requested page.

## Development

```bash
uv sync --dev
uv run ruff format .
uv run ruff check
uv run ty check src tests
uv run pytest
```

You can override the API base URL with `FAB_CARD_VAULT_API_BASE` when needed.
