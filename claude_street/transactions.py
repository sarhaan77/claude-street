import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Transaction history commands.")
console = Console()


def _format_transactions(data: list) -> None:
    if not data:
        console.print("[dim]No transactions found[/dim]")
        return
    table = Table(title="Transactions")
    table.add_column("ID")
    table.add_column("Date")
    table.add_column("Type")
    table.add_column("Description")
    table.add_column("Amount", justify="right")
    for txn in data:
        table.add_row(
            str(txn.get("activityId", "")),
            txn.get("tradeDate", txn.get("settlementDate", ""))[:10],
            txn.get("type", ""),
            txn.get("description", ""),
            f"${txn.get('netAmount', 0):,.2f}",
        )
    console.print(table)


@app.command("list")
def list_transactions(
    account: str = typer.Argument(help="Encrypted account hash"),
    start_date: str = typer.Option(
        None, "--from", help="Start date (yyyy-MM-dd'T'HH:mm:ss.SSSZ)"
    ),
    end_date: str = typer.Option(None, "--to", help="End date"),
    types: str = typer.Option(
        None, "--type", help="Transaction type (TRADE, DIVIDEND, etc)"
    ),
    symbol: str = typer.Option(None, "--symbol", help="Filter by symbol"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List transactions for an account."""
    client = get_client()
    params = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    if types:
        params["types"] = types
    if symbol:
        params["symbol"] = symbol
    resp = client.trader_get(f"/accounts/{account}/transactions", params=params)
    output_response(resp.json(), json_output, _format_transactions)


@app.command("get")
def get_transaction(
    account: str = typer.Argument(help="Encrypted account hash"),
    transaction_id: str = typer.Argument(help="Transaction ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get a specific transaction by ID."""
    client = get_client()
    resp = client.trader_get(f"/accounts/{account}/transactions/{transaction_id}")
    output_response(resp.json(), json_output)
