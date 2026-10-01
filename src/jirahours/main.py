from pathlib import Path

import click
from dotenv import load_dotenv

from jirahours.jira_backend import JiraBackend
from jirahours.timesheet import Timesheet
from jirahours.timesheet.implementations import StdlibTimesheet


@click.group()
@click.version_option()
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
    help="Path to the CSV file containing the hours to check.",
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
    help="Path to the CSV file containing the hours to submit.",
)
def submit(host: str, username: str, api_key: str, csvfile: Path) -> None:
    """Submit hours from the CSV file to Jira."""
    data = _read_and_display_csv_summary(csvfile)
    _send_to_jira(data, host, username, api_key)


def _read_and_display_csv_summary(csvfile: Path) -> Timesheet:
    """Read CSV file and display summary of hour data."""
    click.echo("")
    click.echo(f"Reading csv file '{csvfile}'")
    data: Timesheet = StdlibTimesheet(csvfile)
    # Built before echoing anything, so that a rejected file reports its error
    # straight after the line above rather than after a stray blank line.
    summary = data.summary()
    click.echo("")
    click.echo(summary)
    return data


def _send_to_jira(data: Timesheet, host: str, username: str, api_key: str) -> None:
    click.echo("")
    click.confirm("Do you want to send hours to Jira?", abort=True)
    click.echo(f"Starting to send data")
    jb = JiraBackend(host, username, api_key)
    for worklog in data.worklogs():
        click.echo(f"{worklog.line}: Sending line ")
        r = jb.add_worklog_to_ticket(
            worklog.ticket, worklog.started, worklog.seconds, worklog.description
        )
        click.echo(f"{worklog.line}: {r.status_code}, {r.url}, {r.text}")


def start() -> None:
    load_dotenv()
    cli()
