import pathlib
from datetime import timedelta
from pathlib import Path

import click

from jirahours.csv_reader import read_csv
from jirahours.hour_entries import HourEntries
from jirahours.jira_backend import JiraBackend
from jirahours.summaries import hours_per_day, hours_per_ticket, rows


@click.option(
    "-h",
    "--host",
    prompt=True,
    type=str,
    help="Atlassian host",
)
@click.option(
    "-u",
    "--username",
    prompt=True,
    type=str,
    help="Atlassian username",
)
@click.option(
    "-p",
    "--api-key",
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
        path_type=pathlib.Path,
    ),
)
@click.command()
def cli(host: str, username: str, api_key: str, csvfile: Path) -> None:
    """A over-engineered script to move hours from a CSV file to Jira."""

    # MASTER DATA
    data = HourEntries()

    # READ CSV
    click.echo("")
    click.echo(f"Reading csv file '{csvfile}'")
    read_csv(csvfile, data)

    # PRINT SUMMARIES
    click.echo("")
    click.echo(rows(data))
    click.echo("")
    click.echo(hours_per_day(data))
    click.echo("")
    click.echo(hours_per_ticket(data))

    # SEND TO JIRA
    send_to_jira(data, host, username, api_key)


def send_to_jira(data: HourEntries, host: str, username: str, api_key: str) -> None:
    click.echo("")
    click.confirm("Do you want to send hours to Jira?", abort=True)
    click.echo(f"Starting to send data")
    jb = JiraBackend(host, username, api_key)
    for each in data.entries:
        if each.skip():
            click.echo(f"{each.line}: empty row")
            continue
        click.echo(f"{each.line}: Sending line ")
        r = jb.add_worklog_to_ticket(each)
        click.echo(f"{each.line}: {r.status_code}, {r.url}, {r.text}")


def start() -> None:
    cli(auto_envvar_prefix="JH")
