import typer

from claude_street import (
    accounts,
    hours,
    instruments,
    movers,
    options,
    orders,
    pricehistory,
    quotes,
    streamer,
    transactions,
)
from claude_street.auth import app as auth_app

app = typer.Typer(
    name="claude-street",
    help="CLI for the Schwab Individual Developer API (Trader + Market Data).",
    no_args_is_help=True,
)

app.add_typer(auth_app, name="auth")
app.add_typer(accounts.app, name="accounts")
app.add_typer(orders.app, name="orders")
app.add_typer(transactions.app, name="transactions")
app.add_typer(quotes.app, name="quotes")
app.add_typer(instruments.app, name="instruments")
app.add_typer(options.app, name="options")
app.add_typer(pricehistory.app, name="history")
app.add_typer(movers.app, name="movers")
app.add_typer(hours.app, name="hours")
app.add_typer(streamer.app, name="stream")
