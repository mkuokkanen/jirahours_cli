import pathlib
from pathlib import Path

import click

from jirahours.csv_reader import read_csv
from jirahours.hour_entry import HourEntry
from jirahours.jira_backend import JiraBackend


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
    # DEBUG
    click.echo(f"Reading csv file '{csvfile}'")

    # READ CSV
    data: list[HourEntry] = read_csv(csvfile)

    # PRINT DATA
    click.echo("Data from csv file")
    for each in data:
        if each.skip():
            click.echo(f"{each.line}: empty row")
            continue
        click.echo(
            f"{each.line}: "
            f"{each.started} ({each.date_cell}), "
            f"{each.seconds} ({each.hours_cell}), "
            f"'{each.ticket}', "
            f"'{each.description}'"
        )

    # CONFIRM
    click.confirm("Do you want to continue?", abort=True)

    # SEND DATA
    click.echo(f"Starting to send data")
    jb = JiraBackend(host, username, api_key)

    for each in data:
        if each.skip():
            click.echo(f"{each.line}: empty row")
            continue
        click.echo(f"{each.line}: Sending line ")
        r = jb.add_worklog_to_ticket(each)
        click.echo(f"{each.line}: {r.status_code}, {r.url}, {r.text}")


def start() -> None:
    cli(auto_envvar_prefix="JH")
