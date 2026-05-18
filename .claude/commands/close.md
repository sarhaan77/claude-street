---
description: Close a position (full or partial), record realized P/L
argument_name: description
---

You are a trading execution assistant. The user wants to close a position: $ARGUMENTS

Read CLAUDE.md → "Data Layer" and "Load-bearing invariants" before proceeding. Same five rules as `/trade`, plus this skill computes realized P/L using FIFO matching against OPEN trades.

## Phase 1 — Parse the request

Extract:
- Symbol or OCC option string
- Whether it's a full close (default) or partial — and if partial, qty or fraction
- Reason for closing (this becomes `realized.exit_reason` — choose from CLAUDE.md's enum)
- Order type (market default; limit if user specifies a price)

If the user just says "close NVDA" — assume full market close, ask for the exit_reason if not obvious from context.

## Phase 2 — Sync-on-read

Run the **Sync-on-read protocol** from CLAUDE.md. After it completes, also pull `uv run main.py accounts get HASH --json` for the live position qty (the protocol pulls orders, not positions).

Then:

## Phase 3 — Find the OPEN trades to close

From `data/trades.json`, find all records where:
- `intent == "OPEN"`
- `instrument.symbol == <target>` (exact match — for options, exact OCC string)
- `fill.status == "FILLED"`
- The cumulative qty has not been fully closed by prior CLOSE records

Specifically, the **remaining open qty** for an OPEN trade T is:
```
T.fill.filled_qty − sum(entry.qty_consumed for all CLOSE records where any opens_closed[].open_id == T.id)
```
(See CLAUDE.md → Derived values.)

If no OPEN trades match, cross-check Schwab's `accounts get` positions. Three cases:
- **Schwab has the position, local does not** → orphan position with no recorded thesis. Tell the user, ask if they want to record a synthetic OPEN before closing (they need a TID first).
- **Local has the position, Schwab does not** → likely closed outside this tool, or expired/assigned. Ask the user what happened; offer to back-fill a CLOSE record with `exit_reason: "DISCRETIONARY"` or `EXPIRY` / `ASSIGNMENT`.
- **Neither has the position** → tell the user there's nothing to close.

## Phase 4 — FIFO match

Walk OPEN trades for this symbol in chronological order (`timestamps.filled_at` ascending). Allocate the close qty across them until satisfied. Record the allocation as a list of `{ "open_id": "T-...", "qty_consumed": <num>, "open_avg_fill_price": <num> }`. This is the exact shape of `opens_closed` in the schema and makes partial-close round-tripping work — `/portfolio` reads `qty_consumed` to compute remaining open qty.

If the close qty exceeds total available open qty, refuse — the user is trying to close more than they own.

## Phase 5 — Pull market data

```
uv run main.py quotes get SYMBOL --json
```

For options, use the OCC symbol. Compute the `reference_price` for slippage tracking.

## Phase 6 — Preview & confirm

Build the order JSON. Side is:
- `SELL` for closing a long equity/ETF
- `SELL_TO_CLOSE` for closing a long option
- `BUY_TO_CLOSE` for closing a short option (only relevant once shorting is in scope)

```
uv run main.py orders preview HASH 'ORDER_JSON' --json
```

Show the user:
- Instrument, side, qty, order type, limit/stop, TIF
- Expected proceeds incl. fees
- **Estimated realized P/L** computed from FIFO match: `sum_per_open(qty_consumed × (reference_price − open_avg_fill_price)) − fees`. Show as $ and %.
- Holding period of the longest leg being closed
- Linked thesis (TID) and the close's exit_reason

Stop and ask: "Place this close? (yes / no / change X)" — explicit yes required.

## Phase 7 — Place

```
uv run main.py orders place HASH 'ORDER_JSON' --json
```

Capture `order_id`. If error or no order_id, do NOT write the record.

## Phase 8 — Record the CLOSE trade

Append a new trade record (don't mutate the OPEN records — see CLAUDE.md, no bidirectional pointers). Schema:

- `id` — next sequential `T-<YYYY>-<NNNN>`
- `thesis_id` — same as the OPEN trades being closed (all should match; if they don't, that's a user error — ask)
- `intent: "CLOSE"`
- `side` — see above
- `instrument` — same as the opens (verbatim)
- `order` — built and placed in Phase 6/7, includes `schwab_order_id`
- `timestamps.submitted_at`, `fill.status` (PENDING or FILLED depending on response), `fill.filled_qty`, `fill.avg_fill_price`, `fill.reference_price`
- `rationale` — why exit now
- `exit_plan: null` (closes don't need one)
- `opens_closed` — array of FIFO entries from Phase 4 (objects with `open_id`, `qty_consumed`, `open_avg_fill_price`), in chronological order
- `realized` — `{ pnl, pnl_pct, holding_period_days, exit_reason }`. Compute pnl on actual `avg_fill_price` if status is FILLED. If status is PENDING, leave `realized: null` and let the next sync-on-read fill it in (note in CLAUDE.md update may be needed if sync logic doesn't currently compute realized on transition — see Phase 9).

## Phase 9 — Deferred realized P/L

If the close is still PENDING when this skill exits, the realized P/L numbers are best-effort. The Sync-on-read protocol in CLAUDE.md handles the FILLED transition: it recomputes `realized.pnl`, `realized.pnl_pct`, and `realized.holding_period_days` using the actual `fill.avg_fill_price` and the per-leg `qty_consumed` / `open_avg_fill_price` stored in `opens_closed`. So the data needed to recompute later is already in this record — just leave `realized` populated with the best-effort values and let the protocol overwrite them on the next read.

Tell the user: "P/L will be finalized on next `/portfolio` once the order fills."

## Phase 10 — Offer to archive the thesis

If the close fully exits the thesis (no remaining FILLED OPEN trades for any symbol with `thesis_id == X` after this close), suggest: "This was the last position in `<TID>`. Want to archive the thesis with `/thesis archive <TID>`?"

## Failure modes

- Trying to close more than is held → refuse, show the available qty.
- Schwab/local position mismatch → surface it, don't paper over.
- `orders place` errors → report verbatim, do not write the record.
