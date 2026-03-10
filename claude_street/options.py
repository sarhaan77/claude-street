import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Option chains and expirations.")
console = Console()


def _format_chain(data: dict) -> None:
    console.print(f"[bold]{data.get('symbol', '')} Option Chain[/bold]")
    console.print(
        f"Strategy: {data.get('strategy', '')}, Underlying: ${data.get('underlyingPrice', 0):,.2f}\n"
    )

    for side in ("callExpDateMap", "putExpDateMap"):
        side_label = "CALLS" if "call" in side else "PUTS"
        date_map = data.get(side, {})
        if not date_map:
            continue
        for exp_date, strikes in date_map.items():
            table = Table(title=f"{side_label} - {exp_date}")
            table.add_column("Strike", justify="right")
            table.add_column("Bid", justify="right")
            table.add_column("Ask", justify="right")
            table.add_column("Last", justify="right")
            table.add_column("Volume", justify="right")
            table.add_column("OI", justify="right")
            table.add_column("IV", justify="right")
            table.add_column("Delta", justify="right")
            for strike, options in strikes.items():
                opt = options[0] if options else {}
                table.add_row(
                    strike,
                    f"{opt.get('bid', 0):.2f}",
                    f"{opt.get('ask', 0):.2f}",
                    f"{opt.get('last', 0):.2f}",
                    str(opt.get("totalVolume", 0)),
                    str(opt.get("openInterest", 0)),
                    f"{opt.get('volatility', 0):.2f}%",
                    f"{opt.get('delta', 0):.4f}",
                )
            console.print(table)
            console.print()


def _format_expirations(data: dict) -> None:
    exp_list = data.get("expirationList", [])
    if not exp_list:
        console.print("[dim]No expirations found[/dim]")
        return
    table = Table(title="Option Expirations")
    table.add_column("Expiration Date")
    table.add_column("Days to Expiration", justify="right")
    table.add_column("Type")
    for exp in exp_list:
        table.add_row(
            exp.get("expirationDate", ""),
            str(exp.get("daysToExpiration", "")),
            exp.get("expirationType", ""),
        )
    console.print(table)


@app.command("chain")
def option_chain(
    symbol: str = typer.Argument(help="Underlying symbol"),
    contract_type: str = typer.Option(None, "--type", help="CALL, PUT, or ALL"),
    strike_count: int = typer.Option(
        None, "--strikes", help="Number of strikes above/below ATM"
    ),
    from_date: str = typer.Option(
        None, "--from", help="Expiration from date (yyyy-MM-dd)"
    ),
    to_date: str = typer.Option(None, "--to", help="Expiration to date (yyyy-MM-dd)"),
    strategy: str = typer.Option(
        "SINGLE", "--strategy", help="SINGLE, ANALYTICAL, etc"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get option chain for a symbol."""
    client = get_client()
    params = {"symbol": symbol, "strategy": strategy}
    if contract_type:
        params["contractType"] = contract_type
    if strike_count:
        params["strikeCount"] = strike_count
    if from_date:
        params["fromDate"] = from_date
    if to_date:
        params["toDate"] = to_date
    resp = client.market_get("/chains", params=params)
    output_response(resp.json(), json_output, _format_chain)


@app.command("expirations")
def expiration_chain(
    symbol: str = typer.Argument(help="Underlying symbol"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get option expiration dates for a symbol."""
    client = get_client()
    resp = client.market_get("/expirationchain", params={"symbol": symbol})
    output_response(resp.json(), json_output, _format_expirations)
