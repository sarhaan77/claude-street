import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Price history (OHLCV) commands.")
console = Console()


def _format_candles(data: dict) -> None:
    symbol = data.get("symbol", "")
    candles = data.get("candles", [])
    if not candles:
        console.print("[dim]No price history data[/dim]")
        return
    table = Table(title=f"{symbol} Price History ({len(candles)} candles)")
    table.add_column("Date")
    table.add_column("Open", justify="right")
    table.add_column("High", justify="right")
    table.add_column("Low", justify="right")
    table.add_column("Close", justify="right")
    table.add_column("Volume", justify="right")
    for c in candles[-50:]:
        from datetime import datetime, timezone

        dt = datetime.fromtimestamp(c["datetime"] / 1000, tz=timezone.utc)
        table.add_row(
            dt.strftime("%Y-%m-%d %H:%M"),
            f"{c.get('open', 0):,.2f}",
            f"{c.get('high', 0):,.2f}",
            f"{c.get('low', 0):,.2f}",
            f"{c.get('close', 0):,.2f}",
            f"{c.get('volume', 0):,}",
        )
    if len(candles) > 50:
        console.print(f"[dim]Showing last 50 of {len(candles)} candles[/dim]")
    console.print(table)


@app.command("get")
def get_history(
    symbol: str = typer.Argument(help="Stock symbol"),
    period_type: str = typer.Option(
        "month", "--period-type", help="day, month, year, ytd"
    ),
    period: int = typer.Option(None, "--period", help="Number of periods"),
    frequency_type: str = typer.Option(
        None, "--freq-type", help="minute, daily, weekly, monthly"
    ),
    frequency: int = typer.Option(
        None, "--freq", help="Frequency value (1, 5, 10, 15, 30)"
    ),
    start_date: str = typer.Option(
        None, "--from", help="Start date (epoch ms or yyyy-MM-dd)"
    ),
    end_date: str = typer.Option(
        None, "--to", help="End date (epoch ms or yyyy-MM-dd)"
    ),
    need_extended: bool = typer.Option(
        False, "--extended", help="Include extended hours"
    ),
    need_previous_close: bool = typer.Option(
        True, "--prev-close/--no-prev-close", help="Include previous close"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get price history candles for a symbol."""
    client = get_client()
    params = {"symbol": symbol, "periodType": period_type}
    if period is not None:
        params["period"] = period
    if frequency_type:
        params["frequencyType"] = frequency_type
    if frequency is not None:
        params["frequency"] = frequency
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    params["needExtendedHoursData"] = str(need_extended).lower()
    params["needPreviousClose"] = str(need_previous_close).lower()
    resp = client.market_get("/pricehistory", params=params)
    output_response(resp.json(), json_output, _format_candles)
