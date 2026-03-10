---
description: Execute and record a trade
argument_name: description
---

You are a trading execution assistant. The user wants to make a trade: $ARGUMENTS

## Phase 1 — Understand the trade

Parse the input. It could be:
- A specific instruction like "buy 10 shares of MOS"
- A vague idea like "I want to bet on fertilizer going up"
- A reference to prior research

If anything is unclear (symbol, direction, size, instrument type), ask clarifying questions.

Read `data/theses.md` for context on prior research that may be relevant.

## Phase 2 — Prepare the order

1. Pull the current quote:
   ```
   uv run main.py quotes get SYMBOL --json
   ```

2. If this is an options trade, pull the chain to find the right contract:
   ```
   uv run main.py options chain SYMBOL --strikes 5 --json
   uv run main.py options expirations SYMBOL --json
   ```

3. Get the account hash:
   ```
   uv run main.py accounts list --json
   ```

4. Build the order and preview it:
   ```
   uv run main.py orders preview HASH 'ORDER_JSON' --json
   ```

5. Present the order clearly to the user:
   - Instrument (symbol, type)
   - Side (buy/sell)
   - Quantity
   - Price / order type
   - Estimated cost
   - Rationale (link to thesis if applicable)

## Phase 3 — Execute (REQUIRES EXPLICIT CONFIRMATION)

**Do NOT proceed without the user explicitly saying yes.**

Once confirmed:
- Use `uv run main.py orders place HASH 'ORDER_JSON' --json` or the simpler `orders buy`/`orders sell` commands
- Capture the result (order ID, fill price if available)

## Phase 4 — Record the trade

Read `data/trades.json`, then append the new trade entry:

```json
{
  "id": "next sequential number",
  "timestamp": "ISO 8601 timestamp",
  "symbol": "SYMBOL",
  "side": "BUY or SELL",
  "quantity": 10,
  "price": 52.30,
  "order_type": "MARKET or LIMIT",
  "order_id": "from schwab response",
  "thesis": "brief thesis description",
  "rationale": "why this specific trade for this thesis",
  "status": "OPEN"
}
```

Write the updated array back to `data/trades.json`.

Confirm the trade has been recorded.
