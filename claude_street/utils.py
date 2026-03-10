import json

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def output_json(data) -> None:
    typer.echo(json.dumps(data, indent=2, default=str))


def make_table(title: str, columns: list[str]) -> Table:
    table = Table(title=title, show_lines=True)
    for col in columns:
        table.add_column(col)
    return table


def output_response(data, json_output: bool, formatter=None) -> None:
    if json_output:
        output_json(data)
    elif formatter:
        formatter(data)
    else:
        output_json(data)
