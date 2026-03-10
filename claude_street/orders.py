import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Order management commands.")
console = Console()


def _format_orders(data: list) -> None:
    if not data:
        console.print("[dim]No orders found[/dim]")
        return
    table = Table(title="Orders")
    table.add_column("Order ID")
    table.add_column("Status")
    table.add_column("Type")
    table.add_column("Side")
    table.add_column("Symbol")
    table.add_column("Qty", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Entered")
    for order in data:
        legs = order.get("orderLegCollection", [{}])
        leg = legs[0] if legs else {}
        inst = leg.get("instrument", {})
        table.add_row(
            str(order.get("orderId", "")),
            order.get("status", ""),
            order.get("orderType", ""),
            leg.get("instruction", ""),
            inst.get("symbol", ""),
            str(leg.get("quantity", "")),
            str(order.get("price", order.get("stopPrice", "MARKET"))),
            order.get("enteredTime", "")[:19],
        )
    console.print(table)


def _read_order_json(file_or_json: str) -> dict:
    path = Path(file_or_json)
    if path.exists():
        return json.loads(path.read_text())
    return json.loads(file_or_json)


@app.command("list")
def list_orders(
    account: str = typer.Argument(help="Encrypted account hash"),
    from_date: str = typer.Option(
        None, "--from", help="Start date (yyyy-MM-dd'T'HH:mm:ss.SSSZ)"
    ),
    to_date: str = typer.Option(None, "--to", help="End date"),
    status: str = typer.Option(None, "--status", help="Order status filter"),
    max_results: int = typer.Option(None, "--max", help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List orders for an account."""
    client = get_client()
    params = {}
    if from_date:
        params["fromEnteredTime"] = from_date
    if to_date:
        params["toEnteredTime"] = to_date
    if status:
        params["status"] = status
    if max_results:
        params["maxResults"] = max_results
    resp = client.trader_get(f"/accounts/{account}/orders", params=params)
    output_response(resp.json(), json_output, _format_orders)


@app.command("get")
def get_order(
    account: str = typer.Argument(help="Encrypted account hash"),
    order_id: str = typer.Argument(help="Order ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get a specific order by ID."""
    client = get_client()
    resp = client.trader_get(f"/accounts/{account}/orders/{order_id}")
    output_response(resp.json(), json_output)


@app.command("place")
def place_order(
    account: str = typer.Argument(help="Encrypted account hash"),
    order_json: str = typer.Argument(help="Order JSON string or path to JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Place an order. Accepts a JSON file path or inline JSON."""
    client = get_client()
    order = _read_order_json(order_json)
    resp = client.trader_post(f"/accounts/{account}/orders", json=order)
    result = {"status": "placed", "status_code": resp.status_code}
    location = resp.headers.get("Location", "")
    if location:
        result["order_id"] = location.split("/")[-1]
    output_response(result, json_output)


@app.command("cancel")
def cancel_order(
    account: str = typer.Argument(help="Encrypted account hash"),
    order_id: str = typer.Argument(help="Order ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Cancel a specific order."""
    client = get_client()
    client.trader_delete(f"/accounts/{account}/orders/{order_id}")
    result = {"status": "cancelled", "order_id": order_id}
    output_response(result, json_output)


@app.command("replace")
def replace_order(
    account: str = typer.Argument(help="Encrypted account hash"),
    order_id: str = typer.Argument(help="Order ID to replace"),
    order_json: str = typer.Argument(help="New order JSON string or path to JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Replace an existing order with a new one."""
    client = get_client()
    order = _read_order_json(order_json)
    client.trader_put(f"/accounts/{account}/orders/{order_id}", json=order)
    result = {"status": "replaced", "order_id": order_id}
    output_response(result, json_output)


@app.command("preview")
def preview_order(
    account: str = typer.Argument(help="Encrypted account hash"),
    order_json: str = typer.Argument(help="Order JSON string or path to JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Preview an order (dry run)."""
    client = get_client()
    order = _read_order_json(order_json)
    resp = client.trader_post(f"/accounts/{account}/previewOrder", json=order)
    output_response(resp.json(), json_output)


@app.command("list-all")
def list_all_orders(
    from_date: str = typer.Option(None, "--from", help="Start date"),
    to_date: str = typer.Option(None, "--to", help="End date"),
    status: str = typer.Option(None, "--status", help="Order status filter"),
    max_results: int = typer.Option(None, "--max", help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List orders across all accounts."""
    client = get_client()
    params = {}
    if from_date:
        params["fromEnteredTime"] = from_date
    if to_date:
        params["toEnteredTime"] = to_date
    if status:
        params["status"] = status
    if max_results:
        params["maxResults"] = max_results
    resp = client.trader_get("/orders", params=params)
    output_response(resp.json(), json_output, _format_orders)


@app.command("buy")
def quick_buy(
    account: str = typer.Argument(help="Encrypted account hash"),
    symbol: str = typer.Argument(help="Stock symbol"),
    quantity: int = typer.Argument(help="Number of shares"),
    price: float = typer.Option(
        None, "--price", help="Limit price (omit for market order)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Quick market/limit buy for equities."""
    order = {
        "orderType": "LIMIT" if price else "MARKET",
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": "BUY",
                "quantity": quantity,
                "instrument": {"symbol": symbol, "assetType": "EQUITY"},
            }
        ],
    }
    if price:
        order["price"] = str(price)
    client = get_client()
    resp = client.trader_post(f"/accounts/{account}/orders", json=order)
    result = {"status": "placed", "side": "BUY", "symbol": symbol, "quantity": quantity}
    location = resp.headers.get("Location", "")
    if location:
        result["order_id"] = location.split("/")[-1]
    output_response(result, json_output)


@app.command("sell")
def quick_sell(
    account: str = typer.Argument(help="Encrypted account hash"),
    symbol: str = typer.Argument(help="Stock symbol"),
    quantity: int = typer.Argument(help="Number of shares"),
    price: float = typer.Option(
        None, "--price", help="Limit price (omit for market order)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Quick market/limit sell for equities."""
    order = {
        "orderType": "LIMIT" if price else "MARKET",
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": "SELL",
                "quantity": quantity,
                "instrument": {"symbol": symbol, "assetType": "EQUITY"},
            }
        ],
    }
    if price:
        order["price"] = str(price)
    client = get_client()
    resp = client.trader_post(f"/accounts/{account}/orders", json=order)
    result = {
        "status": "placed",
        "side": "SELL",
        "symbol": symbol,
        "quantity": quantity,
    }
    location = resp.headers.get("Location", "")
    if location:
        result["order_id"] = location.split("/")[-1]
    output_response(result, json_output)
