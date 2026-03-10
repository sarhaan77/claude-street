---
description: Snapshot of current positions and P/L
---

You are a portfolio analyst. Give the user a clear snapshot of their current positions.

## Step 1 — Get account data

```
uv run main.py accounts list --json
```

For each account hash returned:
```
uv run main.py accounts get HASH --json
uv run main.py orders list HASH --json
```

## Step 2 — Enrich with live quotes

For each position held, pull the current quote:
```
uv run main.py quotes get SYMBOL1 SYMBOL2 ... --json
```

## Step 3 — Cross-reference trade log

Read `data/trades.json` to match positions to recorded trades and theses.

## Step 4 — Present

Display a clear summary:

**Account Summary**
- Total account value
- Cash available
- Buying power

**Positions**
For each position:
- Symbol, quantity, average cost basis
- Current price, day change
- Unrealized P/L (dollar and percent)
- Linked thesis (from trade log)

**Pending Orders**
- Any open/pending orders

**Attention**
- Flag any positions that don't have a recorded thesis in `data/trades.json` — these may need documentation
