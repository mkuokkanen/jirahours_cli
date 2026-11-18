from collections.abc import Sequence
from contextlib import closing
from pathlib import Path

import click
from dotenv import load_dotenv

from jirahours.submitter.base import Submitter
from jirahours.submitter.jira import JiraSubmitter
from jirahours.timesheet.base import Timesheet, Worklog
from jirahours.timesheet.stdlib.timesheet import StdlibTimesheet
from jirahours.visualizer import console


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
    summary = console.summary(data)
    click.echo("")
    click.echo(summary)
    return data


def _send_to_jira(data: Timesheet, host: str, username: str, api_key: str) -> None:
    click.echo("")
    click.confirm("Do you want to send hours to Jira?", abort=True)
    click.echo(f"Starting to send data")
    with closing(JiraSubmitter(host, username, api_key)) as submitter:
        _send_worklogs(data.worklogs(), submitter)


def _send_worklogs(worklogs: Sequence[Worklog], submitter: Submitter) -> None:
    """Send in order, stopping at the first failure.

    Each result is echoed as it comes back, so an interrupted run still shows
    what was sent.
    """
    sent: list[int] = []
    for worklog in worklogs:
        click.echo(f"{worklog.line}: Sending line ")
        submitted = submitter.add_worklog(worklog)
        click.echo(f"{submitted.line}: {submitted.message}")
        if not submitted.ok:
            raise click.ClickException(
                f"Line {submitted.line} failed. "
                f"Lines sent: {', '.join(map(str, sent)) or 'none'}. "
                "Remove the sent lines from the file before running again, "
                "or they will be sent twice."
            )
        sent.append(submitted.line)


def start() -> None:
    load_dotenv()
    cli()
