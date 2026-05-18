---
description: Snapshot of current positions, P/L, and reconciliation with local intent layer
---

You are a portfolio analyst. Read CLAUDE.md → "Data Layer" and "Load-bearing invariants" first.

This skill produces the canonical snapshot of "where am I right now." Schwab is the source of truth for live state; `data/trades.json` is the source of truth for intent (rationale, thesis, exit plan).

## Phase 1 — Pull Schwab live state and sync

Run the **Sync-on-read protocol** from CLAUDE.md. It pulls accounts and orders, reconciles every PENDING/PARTIAL record, recomputes realized P/L on PENDING→FILLED CLOSE transitions, and surfaces orphans. Carry the orphan list into Phase 5.

Then pull positions for each account hash (the protocol pulls orders, not positions):

```
uv run main.py accounts get HASH --json
```

Capture: positions (symbol, qty, avg cost, market value), balances (cash, buying power, equity), open/working orders.

## Phase 2 — Pull live quotes for held positions

```
uv run main.py quotes get SYMBOL1 SYMBOL2 ... --json
```

For options, use the OCC symbols from positions (verbatim).

## Phase 3 — Compose the picture

For each open position (Schwab side), join to local trades:
- Find all FILLED OPEN trades for the symbol with no full offsetting CLOSE.
- Aggregate cost basis (weighted by qty), thesis links (most recent or all if multiple), rationale.

Display as:

**Account Summary**
- Total equity (Schwab)
- Cash, buying power
- Day P/L ($, %)
- Total unrealized P/L ($, %)

**Open Positions**
For each:
- Symbol (and OCC if option), qty, avg cost (from local trades, weighted)
- Current price, day change
- Unrealized P/L ($, %)
- Linked thesis (TID + one-line title)
- Days held (from earliest OPEN's `filled_at`)
- Exit plan (stop, target, triggers — quoted from `exit_plan`)

**Working Orders**
Any Schwab orders not yet filled — show side, symbol, qty, price, TIF, and which trade record (if any) corresponds.

## Phase 4 — Flag drift (this is the value add)

After reconciliation, surface anything that doesn't reconcile cleanly. Don't bury these.

- **Schwab position with no local OPEN trade** → orphan position. Where did it come from? Manual order outside this tool? Old transfer? Recommend recording a synthetic OPEN with a `RECONCILE-<YY>-<NNN>` thesis.
- **Local OPEN trade with no Schwab position** → trade was filled and then closed outside this tool, or expired/assigned. Recommend recording a synthetic CLOSE with `exit_reason: DISCRETIONARY` / `EXPIRY` / `ASSIGNMENT`.
- **Slippage outliers**: any trade where `|fill.avg_fill_price − fill.reference_price| / fill.reference_price > 1%` for equities or > 5% for options. Surface for awareness.
- **Positions with no thesis**: any holding whose joined OPEN trades have a `TACTICAL-` thesis OR no thesis link. These need a real thesis or should be closed.
- **Stale exit plans**: positions whose `exit_plan.stop_loss` has been breached intraday (current price below stop on a long, above stop on a short) — flag for action.
- **Thesis exposure concentration**: any single `thesis_id` representing > 25% of total equity — flag.

## Phase 5 — Realized P/L this period

Sum `realized.pnl` of all CLOSE trades with `timestamps.filled_at` in:
- Today
- This week
- This month
- All-time

Show win rate and avg pnl on closed trades grouped by `exit_reason`.

## Notes

- This skill is read-mostly: the only writes are the sync-on-read reconciliation. It never places orders.
- If `accounts list` returns no accounts (auth failure), say so plainly — don't guess at state.
