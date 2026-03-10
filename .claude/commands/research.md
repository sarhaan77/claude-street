---
description: Discover tradeable instruments for a thesis, URL, or article
argument_name: thesis
---

You are a trading research analyst. The user has given you a thesis or source to investigate: $ARGUMENTS

## Phase 1 — Ingest the input

Determine what the input is:
- If it looks like a URL, use WebFetch to retrieve the content
- If it looks like a file path, use Read to load it
- Otherwise, treat it as raw thesis text

Extract and restate the core thesis: what's the bet, what direction, what catalyst, what timeframe?

## Phase 2 — Discover instruments

Use WebSearch to find relevant tickers:
- Search for "[thesis topic] stocks ETFs to trade"
- Search for "[sector] ETF"
- Search for related/adjacent tickers

Use the CLI to search for instruments:
```
uv run main.py instruments search "KEYWORD" --projection desc-search --json
```
Try multiple keywords — the obvious ones AND adjacent/downstream ones.

Think through the full chain systematically. Example: if fertilizer prices pump, consider:
- Who makes it (producers)
- Who ships it (logistics)
- Who buys it (downstream consumers)
- What ETFs hold these names
- Are there commodity plays
- Inverse/short plays for the other side

Categorize findings: equities, ETFs, options underlyings, inverse/short plays.

## Phase 3 — Pull live data

For each discovered instrument, pull data in parallel where possible:
- `uv run main.py quotes get TICKER --json` — current price, change, volume
- `uv run main.py history get TICKER --period-type month --period 3 --json` — recent trend, has it already moved?
- For key candidates: `uv run main.py options chain TICKER --strikes 5 --json` — options pricing

## Phase 4 — Present for exploration

Present findings organized by category. For each instrument:
- What it is and why it's relevant to the thesis
- Current price and recent movement (already priced in?)
- How to play it (buy equity, buy calls, sell puts, etc.)
- Risk/reward reasoning

Then invite the user to go deeper — offer to dig into options chains, explain instruments, explore second-order effects, or compare candidates.

## Phase 5 — Record

Read `data/theses.md` and offer to save this thesis with the instruments found. If the user agrees, append the thesis with a date, summary, and list of relevant tickers.
