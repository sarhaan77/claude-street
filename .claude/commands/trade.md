---
description: Open or scale into a position (equity, ETF, or option)
argument_name: description
---

You are a trading execution assistant. The user wants to open a position: $ARGUMENTS

Read CLAUDE.md → "Data Layer" and "Load-bearing invariants" before proceeding. The four rules that matter most here:
1. **No record without an order_id** — never write to `trades.json` until Schwab returns one.
2. **Sync-on-read** — reconcile local PENDING/PARTIAL records with Schwab before reasoning about exposure.
3. **Thesis required** — every trade links to a TID.
4. **OCC symbol verbatim** for options.

## Phase 1 — Parse the request

Extract:
- Direction (long / short)
- Instrument type (equity / ETF / option) — infer from context
- Symbol or underlying
- Sizing intent (shares, dollar amount, % of book, contracts)
- Order type (market default; limit / stop if user specifies a price level)

If anything's ambiguous (especially symbol and quantity), ask a single targeted question. Don't ask 4 questions in a row — pick the one that actually blocks you.

## Phase 2 — Verify the thesis

Get the TID. Path A: user names a TID like `AIINFRA-26-001` → use it. Path B: user references a thesis informally ("the AI infra basket") → grep `data/theses.md` and `data/theses_archive.md` to find a match. Path C: user has no thesis → push back once. If they insist, invoke `/thesis new` first and use the returned TID. (For pure tactical trades, use `TACTICAL-<YY>-<NNN>`.)

Verify the TID exists by grepping both files. If it doesn't, refuse and tell the user to create one.

## Phase 3 — Sync-on-read

Run the **Sync-on-read protocol** from CLAUDE.md before reasoning about current exposure. If any orphan records are surfaced, mention them but don't block the new trade — they're a separate problem.

## Phase 4 — Pull market data and shape the order

For equities/ETFs:
```
uv run main.py quotes get SYMBOL --json
```

For options — pull the chain to find the exact OCC symbol:
```
uv run main.py options expirations SYMBOL --json
uv run main.py options chain SYMBOL --strikes 10 --from-date YYYY-MM-DD --to-date YYYY-MM-DD --json
```

Capture the OCC symbol returned by the chain **verbatim** (preserve any embedded whitespace). That string is what goes into `instrument.symbol` and what Schwab needs in the order.

Compute the `reference_price` (mid for options, last for equities) for the slippage record.

## Phase 5 — Sizing & exposure check

Show the user before placing:

- **Dollar size** — `qty × reference_price × multiplier` (multiplier is 1 for equity, 100 for option)
- **% of buying power** — from the synced `accounts get HASH` response
- **Existing same-symbol exposure** — sum of FILLED open qty for this symbol from `trades.json`
- **Existing same-thesis exposure** — sum of cost basis across all OPEN trades with this `thesis_id`. Flag if adding this trade pushes thesis exposure past 25% of account.

If any of these look wrong (under-funded, hyper-concentrated), say so. Don't just plow ahead.

## Phase 6 — Build the order, preview, confirm

1. Construct the order JSON. Use the templates in `docs/schwab_trader_api_description.md` if you need a reference.

2. Preview:
   ```
   uv run main.py orders preview HASH 'ORDER_JSON' --json
   ```

3. Render the preview clearly:
   - Instrument (symbol + OCC if option)
   - Side, qty, order type, limit/stop, TIF
   - Estimated cost incl. fees
   - Linked thesis (TID + one-line title)
   - Exit plan you intend to record (ask the user: stop level? take-profit? time horizon? thesis-break trigger?)

4. **Stop and ask: "Place this order? (yes / no / change X)"** Do NOT proceed without an explicit "yes."

## Phase 7 — Place

```
uv run main.py orders place HASH 'ORDER_JSON' --json
```

Capture the returned `order_id`. If no `order_id` returns or the call errors, tell the user and **do not write to `trades.json`**.

## Phase 8 — Record the trade

Read `data/trades.json`. Compute the next `id` as `T-<YYYY>-<NNNN>` where YYYY is the current year and NNNN is `max(existing id with same year) + 1`, padded to 4 digits.

Append the record using the schema in CLAUDE.md. Required fields, no shortcuts:
- `id`, `thesis_id`, `intent: "OPEN"`, `side`
- `instrument` block (verbatim OCC for options)
- `order` block including `schwab_order_id`
- `timestamps.submitted_at` (ISO 8601 UTC, now)
- `fill.status: "PENDING"` (or `"FILLED"` if the place response confirms an instant market fill — populate `filled_qty`, `avg_fill_price`, `timestamps.filled_at` from the response)
- `fill.reference_price` from Phase 4
- `rationale` — 1-2 sentence specific reason for THIS entry (not the thesis body — that's already linked)
- `exit_plan` — fill from the user's answers in Phase 6. Nulls are allowed but discourage them.
- `opens_closed: null`, `realized: null`

Write back to `data/trades.json` (whole-file rewrite — preserve formatting; one record per top-level array element).

## Phase 9 — Confirm

Tell the user: trade ID, Schwab order ID, fill status, and what to expect (e.g. "limit order working — `/portfolio` will sync it on next run").

## Failure modes — handle, don't paper over

- **`orders place` errors** → report verbatim, do not write the record.
- **Market closed / instrument not tradable** → tell the user, don't queue silently.
- **Fractional share request on a non-fractionable instrument** → tell the user, suggest whole shares or a dollar-target order.
- **Insufficient buying power** → flag in Phase 5, don't even preview.
