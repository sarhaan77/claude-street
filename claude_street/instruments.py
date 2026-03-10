import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Instrument search and lookup commands.")
console = Console()


def _format_instruments(data: dict) -> None:
    instruments = data.get("instruments", [])
    if not instruments:
        console.print("[dim]No instruments found[/dim]")
        return
    table = Table(title="Instruments")
    table.add_column("Symbol")
    table.add_column("CUSIP")
    table.add_column("Description")
    table.add_column("Type")
    table.add_column("Exchange")
    for inst in instruments:
        table.add_row(
            inst.get("symbol", ""),
            inst.get("cusip", ""),
            inst.get("description", ""),
            inst.get("assetType", ""),
            inst.get("exchange", ""),
        )
    console.print(table)


@app.command("search")
def search_instruments(
    symbol: str = typer.Argument(help="Symbol or search string"),
    projection: str = typer.Option(
        "symbol-search",
        "--projection",
        help="Projection type: symbol-search, symbol-regex, desc-search, desc-regex, search, fundamental",
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Search for instruments by symbol or description."""
    client = get_client()
    resp = client.market_get(
        "/instruments", params={"symbol": symbol, "projection": projection}
    )
    output_response(resp.json(), json_output, _format_instruments)


@app.command("get")
def get_instrument(
    cusip: str = typer.Argument(help="CUSIP identifier"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get instrument details by CUSIP."""
    client = get_client()
    resp = client.market_get(f"/instruments/{cusip}")
    output_response(resp.json(), json_output)
