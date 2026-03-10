import asyncio
import json

import typer
import websockets
from rich.console import Console
from rich.live import Live
from rich.table import Table

from claude_street.auth import get_valid_token
from claude_street.client import get_client

app = typer.Typer(help="WebSocket streaming commands for real-time market data.")
console = Console()


def _get_streamer_info() -> dict:
    client = get_client()
    resp = client.trader_get("/userPreference")
    prefs = resp.json()
    streamer = prefs.get("streamerInfo", [{}])
    if isinstance(streamer, list):
        streamer = streamer[0] if streamer else {}
    return {
        "url": streamer.get("streamerSocketUrl", ""),
        "customer_id": prefs.get(
            "schwabClientCustomerId", streamer.get("schwabClientCustomerId", "")
        ),
        "correl_id": prefs.get(
            "schwabClientCorrelId", streamer.get("schwabClientCorrelId", "")
        ),
    }


def _login_request(customer_id: str, correl_id: str) -> dict:
    return {
        "requests": [
            {
                "requestid": "0",
                "service": "ADMIN",
                "command": "LOGIN",
                "SchwabClientCustomerId": customer_id,
                "SchwabClientCorrelId": correl_id,
                "parameters": {
                    "Authorization": get_valid_token(),
                    "SchwabClientChannel": "client",
                    "SchwabClientFunctionId": "streamer",
                },
            }
        ]
    }


def _subscribe_request(
    service: str,
    keys: str,
    fields: str,
    customer_id: str,
    correl_id: str,
    request_id: str = "1",
) -> dict:
    return {
        "requests": [
            {
                "requestid": request_id,
                "service": service,
                "command": "SUBS",
                "SchwabClientCustomerId": customer_id,
                "SchwabClientCorrelId": correl_id,
                "parameters": {"keys": keys, "fields": fields},
            }
        ]
    }


EQUITY_FIELDS = {
    "0": "Symbol",
    "1": "Bid",
    "2": "Ask",
    "3": "Last",
    "4": "Bid Size",
    "5": "Ask Size",
    "6": "Ask ID",
    "7": "Bid ID",
    "8": "Total Volume",
    "9": "Last Size",
    "10": "High",
    "11": "Low",
    "12": "Close",
    "13": "Exchange",
    "14": "Marginable",
    "15": "Description",
    "16": "Last ID",
    "17": "Open",
    "18": "Net Change",
    "28": "52 High",
    "29": "52 Low",
    "30": "PE Ratio",
    "48": "Security Status",
    "49": "Net % Change",
}


async def _stream_service(
    service: str, keys: str, fields: str, json_output: bool
) -> None:
    info = _get_streamer_info()
    url = info["url"]
    if not url:
        console.print("[red]No streamer URL found. Check user preferences.[/red]")
        return

    if not url.startswith("wss://"):
        url = f"wss://{url}/ws"

    async with websockets.connect(url) as ws:
        login_msg = _login_request(info["customer_id"], info["correl_id"])
        await ws.send(json.dumps(login_msg))
        login_resp = await ws.recv()

        if not json_output:
            resp_data = json.loads(login_resp)
            responses = resp_data.get("response", [])
            if responses and responses[0].get("content", {}).get("code") != 0:
                console.print(
                    f"[red]Login failed: {responses[0].get('content', {})}[/red]"
                )
                return
            console.print("[green]Connected to streamer[/green]")

        sub_msg = _subscribe_request(
            service, keys, fields, info["customer_id"], info["correl_id"]
        )
        await ws.send(json.dumps(sub_msg))

        data_store: dict[str, dict] = {}

        if json_output:
            async for msg in ws:
                parsed = json.loads(msg)
                if "data" in parsed:
                    typer.echo(json.dumps(parsed["data"]))
        else:
            with Live(console=console, refresh_per_second=4) as live:
                async for msg in ws:
                    parsed = json.loads(msg)
                    if "notify" in parsed:
                        continue
                    if "data" in parsed:
                        for svc_data in parsed["data"]:
                            for item in svc_data.get("content", []):
                                key = item.get("key", "?")
                                if key not in data_store:
                                    data_store[key] = {}
                                data_store[key].update(item)

                        table = Table(title=f"{service} (live)")
                        table.add_column("Symbol")
                        table.add_column("Last", justify="right")
                        table.add_column("Bid", justify="right")
                        table.add_column("Ask", justify="right")
                        table.add_column("Volume", justify="right")
                        table.add_column("Change", justify="right")

                        for sym, vals in sorted(data_store.items()):
                            change = vals.get("18", vals.get(18, 0)) or 0
                            color = "green" if change >= 0 else "red"
                            table.add_row(
                                sym,
                                f"{vals.get('3', vals.get(3, 0)) or 0:,.2f}",
                                f"{vals.get('1', vals.get(1, 0)) or 0:,.2f}",
                                f"{vals.get('2', vals.get(2, 0)) or 0:,.2f}",
                                f"{vals.get('8', vals.get(8, 0)) or 0:,}",
                                f"[{color}]{change:+,.2f}[/{color}]",
                            )
                        live.update(table)


def _run_stream(service: str, keys: str, fields: str, json_output: bool) -> None:
    try:
        asyncio.run(_stream_service(service, keys, fields, json_output))
    except KeyboardInterrupt:
        console.print("\n[yellow]Stream stopped.[/yellow]")


@app.command("quotes")
def stream_quotes(
    symbols: list[str] = typer.Argument(help="Stock symbols to stream"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Stream real-time Level 1 equity quotes."""
    keys = ",".join(s.upper() for s in symbols)
    fields = "0,1,2,3,4,5,8,10,11,12,17,18,49"
    _run_stream("LEVELONE_EQUITIES", keys, fields, json_output)


@app.command("options")
def stream_options(
    symbols: list[str] = typer.Argument(help="Option symbols to stream"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Stream real-time Level 1 option quotes."""
    keys = ",".join(s.upper() for s in symbols)
    fields = "0,1,2,3,4,5,8,10,11,19,20,23,24"
    _run_stream("LEVELONE_OPTIONS", keys, fields, json_output)


@app.command("futures")
def stream_futures(
    symbols: list[str] = typer.Argument(help="Futures symbols to stream"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Stream real-time Level 1 futures quotes."""
    keys = ",".join(s.upper() for s in symbols)
    fields = "0,1,2,3,4,5,8,10,11,12,18"
    _run_stream("LEVELONE_FUTURES", keys, fields, json_output)


@app.command("chart")
def stream_chart(
    symbols: list[str] = typer.Argument(help="Equity symbols for chart data"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Stream real-time chart candles (1-minute bars)."""
    keys = ",".join(s.upper() for s in symbols)
    fields = "0,1,2,3,4,5,6,7,8"
    _run_stream("CHART_EQUITY", keys, fields, json_output)


@app.command("activity")
def stream_activity(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Stream account activity (order fills, etc)."""
    info = _get_streamer_info()
    fields = "0,1,2,3"
    _run_stream("ACCT_ACTIVITY", info["customer_id"], fields, json_output)
