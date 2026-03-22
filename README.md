# fab-card-vault-cli

`fab-card-vault-cli` は、[`fab-card-db-mcp`](https://github.com/japan4415/fab-card-db-mcp) の主要機能を、単発実行の CLI として使えるようにした Python ツールです。MCP サーバーを常駐させず、JSON-first の出力で AI エージェントやシェルパイプラインから直接扱えます。

## Setup

```bash
uv sync --dev
```

インストールしてグローバルに使う場合:

```bash
uv tool install .
```

ローカル実行だけならそのまま:

```bash
uv run fab-card-vault --help
```

## Commands

```bash
uv run fab-card-vault search Awakening
uv run fab-card-vault prints awakening-3
uv run fab-card-vault detail awakening-3 --print-id JA_GAP008
uv run fab-card-vault products --page 1
```

既定では標準出力に JSON を返します。人向けに色付きで見たい場合だけ `--format pretty` を付けます。

```bash
uv run fab-card-vault --format pretty search Awakening
```

## jq Examples

カードIDだけ抜く:

```bash
uv run fab-card-vault search Awakening | jq -r '.[0].id'
```

日本語の印刷IDを探す:

```bash
uv run fab-card-vault detail awakening-3 | jq -r '.variants[] | select(.language == "JA") | .printId'
```

製品名だけ並べる:

```bash
uv run fab-card-vault products --page 1 | jq -r '.productGroups[].products[].productName'
```

## Development

```bash
uv run ruff format .
uv run ruff check
uv run ty check src tests
uv run pytest
```

必要に応じて `FAB_CARD_VAULT_API_BASE` で API のベースURLを差し替えられます。

