import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Stock quotes commands.")
console = Console()


def _format_quotes(data: dict) -> None:
    table = Table(title="Quotes")
    table.add_column("Symbol")
    table.add_column("Last", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("% Change", justify="right")
    table.add_column("Bid", justify="right")
    table.add_column("Ask", justify="right")
    table.add_column("Volume", justify="right")
    for symbol, info in data.items():
        quote = info.get("quote", info)
        change = quote.get("netChange", 0)
        color = "green" if change >= 0 else "red"
        table.add_row(
            symbol,
            f"${quote.get('lastPrice', 0):,.2f}",
            f"[{color}]{change:+,.2f}[/{color}]",
            f"[{color}]{quote.get('netPercentChange', 0):+,.2f}%[/{color}]",
            f"${quote.get('bidPrice', 0):,.2f}",
            f"${quote.get('askPrice', 0):,.2f}",
            f"{quote.get('totalVolume', 0):,}",
        )
    console.print(table)


@app.command("get")
def get_quotes(
    symbols: list[str] = typer.Argument(help="One or more stock symbols"),
    fields: str = typer.Option(
        None,
        "--fields",
        help="Comma-separated fields (quote,fundamental,extended,reference,regular)",
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get quotes for one or more symbols."""
    client = get_client()
    params = {"symbols": ",".join(symbols)}
    if fields:
        params["fields"] = fields
    resp = client.market_get("/quotes", params=params)
    output_response(resp.json(), json_output, _format_quotes)


@app.command("lookup")
def lookup_quote(
    symbol: str = typer.Argument(help="Stock symbol"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get detailed quote for a single symbol."""
    client = get_client()
    resp = client.market_get(f"/{symbol}/quotes")
    output_response(resp.json(), json_output, _format_quotes)
