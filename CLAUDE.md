# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

claude-street is a Python CLI for the Schwab Individual Developer API (Trader API). It wraps two Schwab API services:

- **Trader API** (`https://api.schwabapi.com/trader/v1`) — Accounts, Orders, Transactions
- **Market Data API** (`https://api.schwabapi.com/marketdata/v1`) — Quotes, Option Chains, Price History, Movers, Market Hours, Instruments

API reference docs live in `docs/`:

- `schwab_trader_api_spec.json` — OpenAPI spec for accounts, orders, and transactions endpoints
- `schwab_trader_api_description.md` — OAuth 2.0 three-legged flow walkthrough and order placement examples
- `schwab_market_data_api_spec.json` — OpenAPI spec for quotes, option chains, price history, movers, market hours, and instruments
- `schwab_streamer_api_description.md` — WebSocket Streamer API docs for real-time market data and account activity

## Development Commands

This project uses **uv** exclusively for package management. Never use pip, poetry, or conda.

```bash
uv sync                      # Install/sync dependencies
uv add <package>             # Add a dependency
uv run main.py                  # Run the CLI, imp it is not `uv run python ...`, it is `uv run ...`
uv run pytest                # Run tests
uv run pytest path/to/test.py::test_name  # Run a single test
uv run ruff check .          # Lint
uv run ruff format .         # Format
```

## Key Constraints

- Python >=3.13 (pinned in `.python-version`)
- The project is in early bootstrap stage — `main.py` is the entry point
- Schwab OAuth uses a three-legged flow: authorization code → access token (30 min) → refresh token (7 days)
- Auth base URL: `https://api.schwabapi.com/v1/oauth/`
- Credentials (Client ID, Client Secret, Callback URL) come from Schwab's Dev Portal and must never be committed
- `.env` is gitignored and used for local secrets. SCHWAB_APP_KEY and SCHWAB_SECRET are in the .env file.

## Trading Intelligence

### Analyst Persona

When the user mentions news, events, or market trends, think through tradeable implications unprompted. For every thesis, systematically consider: individual equities, sector/thematic/commodity ETFs, options, inverse ETFs, futures. Explain WHY each instrument fits the thesis.

Think through: direct plays, second-order effects, adjacent sectors, hedge plays.

Be a teacher — when the user doesn't understand an instrument, explain how it works, how it's priced, what drives it. Don't assume financial literacy.

### CLI Reference

Use these commands via Bash with `--json` for structured output:

```
uv run main.py quotes get SYMBOL1 SYMBOL2 --json
uv run main.py options chain SYMBOL --strikes 10 --json
uv run main.py options expirations SYMBOL --json
uv run main.py history get SYMBOL --period-type year --period 1 --json
uv run main.py instruments search "KEYWORD" --projection desc-search --json
uv run main.py movers get '$SPX' --sort PERCENT_CHANGE_UP --json
uv run main.py accounts list --json
uv run main.py accounts get HASH --json
uv run main.py orders buy HASH SYMBOL QTY --json
uv run main.py orders sell HASH SYMBOL QTY --json
uv run main.py orders preview HASH 'ORDER_JSON' --json
uv run main.py orders place HASH 'ORDER_JSON' --json
uv run main.py orders list HASH --json
```

### Data Files

- `data/trades.json` — append-only trade log. Every trade recorded with timestamp, symbol, side, qty, price, rationale, thesis link.
- `data/theses.md` — active trading theses. Read before research sessions for context.

### Safety

- NEVER place orders without explicit user confirmation
- Always show the exact order and explain it before execution
- Always use `orders preview` before `orders place`
