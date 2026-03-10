import typer
from rich.console import Console
from rich.table import Table

from claude_street.client import get_client
from claude_street.utils import output_response

app = typer.Typer(help="Market hours commands.")
console = Console()


def _format_hours(data: dict) -> None:
    for market_type, markets in data.items():
        for market_name, info in markets.items():
            if isinstance(info, dict):
                table = Table(title=f"{market_name}")
                table.add_column("Field")
                table.add_column("Value")
                table.add_row("Market", info.get("marketType", ""))
                table.add_row("Product", info.get("product", ""))
                table.add_row("Is Open", str(info.get("isOpen", "")))
                session = info.get("sessionHours", {})
                for session_type, hours_list in session.items():
                    if isinstance(hours_list, list):
                        for h in hours_list:
                            table.add_row(
                                f"{session_type}",
                                f"{h.get('start', '')} - {h.get('end', '')}",
                            )
                console.print(table)
                console.print()


@app.command("list")
def list_hours(
    date: str = typer.Option(None, "--date", help="Date (yyyy-MM-dd)"),
    markets: str = typer.Option(
        None, "--markets", help="Comma-separated: equity,option,bond,future,forex"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get market hours for all markets."""
    client = get_client()
    params = {}
    if date:
        params["date"] = date
    if markets:
        params["markets"] = markets
    resp = client.market_get("/markets", params=params)
    output_response(resp.json(), json_output, _format_hours)


@app.command("get")
def get_hours(
    market: str = typer.Argument(
        help="Market type: equity, option, bond, future, forex"
    ),
    date: str = typer.Option(None, "--date", help="Date (yyyy-MM-dd)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get market hours for a specific market."""
    client = get_client()
    params = {}
    if date:
        params["date"] = date
    resp = client.market_get(f"/markets/{market}", params=params)
    output_response(resp.json(), json_output, _format_hours)
