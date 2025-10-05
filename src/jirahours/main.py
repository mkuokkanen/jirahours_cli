from pathlib import Path

import click
from dotenv import load_dotenv

from jirahours.csv_reader import csv_file_to_hours
from jirahours.jira_backend import JiraBackend
from jirahours.model import Hours
from jirahours.summarizers import hours_per_day, hours_per_ticket, rows


@click.group()
def cli() -> None:
    """An overengineered script to move hours from a CSV file to Jira."""
    pass


@cli.command()
@click.argument(
    "csvfile",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
)
def check(csvfile: Path) -> None:
    """Check and display a summary of hours from the CSV file."""
    _read_and_display_csv_summary(csvfile)


@cli.command()
@click.option(
    "-h",
    "--host",
    envvar="JIRA_HOST",
    prompt=True,
    type=str,
    help="Atlassian host",
)
@click.option(
    "-u",
    "--username",
    envvar="JIRA_USERNAME",
    prompt=True,
    type=str,
    help="Atlassian username",
)
@click.option(
    "-p",
    "--api-key",
    envvar="JIRA_API_KEY",
    prompt=True,
    hide_input=True,
    type=str,
    help="Atlassian token",
)
@click.argument(
    "csvfile",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
)
def submit(host: str, username: str, api_key: str, csvfile: Path) -> None:
    """Submit hours from the CSV file to Jira."""
    data = _read_and_display_csv_summary(csvfile)
    _send_to_jira(data, host, username, api_key)


def _read_and_display_csv_summary(csvfile: Path) -> Hours:
    """Read CSV file and display summary of hour data."""
    click.echo("")
    click.echo(f"Reading csv file '{csvfile}'")
    data = csv_file_to_hours(csvfile)
    click.echo("")
    click.echo(rows(data))
    click.echo("")
    click.echo(hours_per_day(data))
    click.echo("")
    click.echo(hours_per_ticket(data))
    return data


def _send_to_jira(data: Hours, host: str, username: str, api_key: str) -> None:
    click.echo("")
    click.confirm("Do you want to send hours to Jira?", abort=True)
    click.echo(f"Starting to send data")
    jb = JiraBackend(host, username, api_key)
    for entry in data.entries:
        if entry.skip():
            click.echo(f"{entry.line}: empty row")
            continue
        click.echo(f"{entry.line}: Sending line ")
        r = jb.add_worklog_to_ticket(
            entry.ticket, entry.started, entry.seconds, entry.description
        )
        click.echo(f"{entry.line}: {r.status_code}, {r.url}, {r.text}")


def start() -> None:
    load_dotenv()
    cli()
