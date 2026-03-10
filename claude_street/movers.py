import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Market movers commands.")
console = Console()


def _format_movers(data: dict) -> None:
    screeners = data.get("screeners", [])
    if not screeners:
        console.print("[dim]No movers data[/dim]")
        return
    table = Table(title="Market Movers")
    table.add_column("Symbol")
    table.add_column("Description")
    table.add_column("Last", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("% Change", justify="right")
    table.add_column("Volume", justify="right")
    for m in screeners:
        change = m.get("netChange", 0)
        color = "green" if change >= 0 else "red"
        table.add_row(
            m.get("symbol", ""),
            m.get("description", "")[:40],
            f"${m.get('lastPrice', 0):,.2f}",
            f"[{color}]{change:+,.2f}[/{color}]",
            f"[{color}]{m.get('netPercentChange', 0):+,.2f}%[/{color}]",
            f"{m.get('totalVolume', 0):,}",
        )
    console.print(table)


@app.command("get")
def get_movers(
    index: str = typer.Argument(
        help="Index symbol ($DJI, $COMPX, $SPX, NYSE, NASDAQ, OTCBB, INDEX_ALL, EQUITY_ALL, OPTION_ALL, OPTION_PUT, OPTION_CALL)"
    ),
    sort: str = typer.Option(
        None,
        "--sort",
        help="Sort by: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN",
    ),
    frequency: int = typer.Option(
        None, "--freq", help="Frequency: 0 (all), 1, 5, 10, 30, 60"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get top movers for an index."""
    client = get_client()
    params = {}
    if sort:
        params["sort"] = sort
    if frequency is not None:
        params["frequency"] = frequency
    resp = client.market_get(f"/movers/{index}", params=params)
    output_response(resp.json(), json_output, _format_movers)
