import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Account information and user preferences.")
console = Console()


def _format_accounts(data: list) -> None:
    table = Table(title="Accounts")
    table.add_column("Account #")
    table.add_column("Type")
    table.add_column("Net Liquidation")
    table.add_column("Cash Balance")
    for acct in data:
        info = acct.get("securitiesAccount", {})
        balances = info.get("currentBalances", {})
        table.add_row(
            str(info.get("accountNumber", "")),
            info.get("type", ""),
            f"${balances.get('liquidationValue', 0):,.2f}",
            f"${balances.get('cashBalance', 0):,.2f}",
        )
    console.print(table)


def _format_positions(data: dict) -> None:
    info = data.get("securitiesAccount", {})
    positions = info.get("positions", [])
    console.print(
        Panel(f"Account: {info.get('accountNumber', '')} ({info.get('type', '')})")
    )

    if not positions:
        console.print("[dim]No positions[/dim]")
        return

    table = Table(title="Positions")
    table.add_column("Symbol")
    table.add_column("Qty", justify="right")
    table.add_column("Avg Price", justify="right")
    table.add_column("Market Value", justify="right")
    table.add_column("P/L Day", justify="right")
    for pos in positions:
        inst = pos.get("instrument", {})
        table.add_row(
            inst.get("symbol", ""),
            str(pos.get("longQuantity", 0) or pos.get("shortQuantity", 0)),
            f"${pos.get('averagePrice', 0):,.2f}",
            f"${pos.get('marketValue', 0):,.2f}",
            f"${pos.get('currentDayProfitLoss', 0):,.2f}",
        )
    console.print(table)


def _format_account_numbers(data: list) -> None:
    table = Table(title="Account Numbers")
    table.add_column("Account Number")
    table.add_column("Hash Value")
    for item in data:
        table.add_row(str(item.get("accountNumber", "")), item.get("hashValue", ""))
    console.print(table)


@app.command("list")
def list_accounts(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List all linked accounts with balances."""
    client = get_client()
    resp = client.trader_get("/accounts", params={"fields": "positions"})
    output_response(resp.json(), json_output, _format_accounts)


@app.command("get")
def get_account(
    account: str = typer.Argument(help="Encrypted account hash"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get a single account with positions and balances."""
    client = get_client()
    resp = client.trader_get(f"/accounts/{account}", params={"fields": "positions"})
    output_response(resp.json(), json_output, _format_positions)


@app.command("numbers")
def account_numbers(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get account number to encrypted hash mapping."""
    client = get_client()
    resp = client.trader_get("/accounts/accountNumbers")
    output_response(resp.json(), json_output, _format_account_numbers)


@app.command("preferences")
def user_preferences(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get user preferences and streamer subscription keys."""
    client = get_client()
    resp = client.trader_get("/userPreference")
    output_response(resp.json(), json_output)
