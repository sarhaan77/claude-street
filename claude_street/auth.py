import base64
import json
import time
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import typer
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

app = typer.Typer(help="Authentication commands for Schwab API.")
console = Console()

TOKEN_DIR = Path.home() / ".claude-street"
TOKEN_FILE = TOKEN_DIR / "tokens.json"
AUTH_BASE = "https://api.schwabapi.com/v1/oauth"


def _get_credentials() -> tuple[str, str]:
    import os

    app_key = os.environ.get("SCHWAB_APP_KEY")
    secret = os.environ.get("SCHWAB_SECRET")
    if not app_key or not secret:
        raise typer.BadParameter("SCHWAB_APP_KEY and SCHWAB_SECRET must be set in .env")
    return app_key, secret


def _get_callback_url() -> str:
    import os

    return os.environ.get("SCHWAB_CALLBACK_URL", "https://127.0.0.1:5556/callback")


def _save_tokens(data: dict) -> None:
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    data["saved_at"] = time.time()
    TOKEN_FILE.write_text(json.dumps(data, indent=2))


def load_tokens() -> dict | None:
    if not TOKEN_FILE.exists():
        return None
    return json.loads(TOKEN_FILE.read_text())


def _token_expired(tokens: dict) -> bool:
    saved_at = tokens.get("saved_at", 0)
    expires_in = tokens.get("expires_in", 1800)
    return time.time() > saved_at + expires_in - 60


def _exchange_code(code: str) -> dict:
    app_key, secret = _get_credentials()
    callback_url = _get_callback_url()
    auth_header = base64.b64encode(f"{app_key}:{secret}".encode()).decode()
    resp = httpx.post(
        f"{AUTH_BASE}/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": callback_url,
        },
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(tokens: dict | None = None) -> dict:
    if tokens is None:
        tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        raise typer.BadParameter("No refresh token available. Run 'auth login' first.")
    app_key, secret = _get_credentials()
    auth_header = base64.b64encode(f"{app_key}:{secret}".encode()).decode()
    resp = httpx.post(
        f"{AUTH_BASE}/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        },
    )
    resp.raise_for_status()
    new_tokens = resp.json()
    if "refresh_token" not in new_tokens:
        new_tokens["refresh_token"] = tokens["refresh_token"]
    _save_tokens(new_tokens)
    return new_tokens


def get_valid_token() -> str:
    tokens = load_tokens()
    if not tokens:
        raise typer.BadParameter("Not authenticated. Run 'auth login' first.")
    if _token_expired(tokens):
        tokens = refresh_access_token(tokens)
    return tokens["access_token"]


@app.command()
def login() -> None:
    """Start the OAuth login flow. Opens browser for Schwab authorization."""
    app_key, _ = _get_credentials()
    callback_url = _get_callback_url()
    auth_url = (
        f"{AUTH_BASE}/authorize?client_id={app_key}"
        f"&redirect_uri={callback_url}"
        f"&response_type=code"
    )
    console.print("[bold]Opening browser for authorization...[/bold]")
    console.print(f"If it doesn't open, visit:\n{auth_url}")
    webbrowser.open(auth_url)

    console.print(
        "\n[yellow]After authorizing, paste the full callback URL here:[/yellow]"
    )
    callback_input = typer.prompt("Callback URL")
    parsed = urlparse(callback_input)
    qs = parse_qs(parsed.query)
    code = qs.get("code", [None])[0]
    if not code:
        console.print("[red]No authorization code found in URL.[/red]")
        raise typer.Exit(1)

    tokens = _exchange_code(code)
    _save_tokens(tokens)
    console.print("[green]Login successful! Tokens saved.[/green]")


@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Show current authentication status."""
    tokens = load_tokens()
    if not tokens:
        if json_output:
            typer.echo(json.dumps({"authenticated": False}))
        else:
            console.print("[red]Not authenticated. Run 'auth login'.[/red]")
        return

    saved_at = tokens.get("saved_at", 0)
    expires_in = tokens.get("expires_in", 1800)
    remaining = max(0, int(saved_at + expires_in - time.time()))
    expired = remaining == 0

    info = {
        "authenticated": True,
        "token_type": tokens.get("token_type", "Bearer"),
        "expires_in_seconds": remaining,
        "expired": expired,
        "has_refresh_token": "refresh_token" in tokens,
    }
    if json_output:
        typer.echo(json.dumps(info))
    else:
        status_color = "red" if expired else "green"
        console.print("[bold]Auth Status[/bold]")
        console.print(
            f"  Authenticated: [{status_color}]{not expired}[/{status_color}]"
        )
        console.print(f"  Token expires in: {remaining}s")
        console.print(
            f"  Refresh token: {'Yes' if info['has_refresh_token'] else 'No'}"
        )


@app.command()
def refresh(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Refresh the access token using the stored refresh token."""
    tokens = refresh_access_token()
    if json_output:
        typer.echo(
            json.dumps({"refreshed": True, "expires_in": tokens.get("expires_in")})
        )
    else:
        console.print("[green]Token refreshed successfully.[/green]")
