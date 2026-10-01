"""This implementation's take on showing the file back to the user.

Plain string building over the parsed entries. Another implementation may well
render differently, and is allowed to.
"""

from jirahours.timesheet.implementations.stdlib._model import Hours


def summary(hours: Hours) -> str:
    """Every section, blank line separated."""
    return "\n\n".join(
        [
            format_lines(hours),
            format_hours_per_day(hours),
            format_hours_per_ticket(hours),
            format_hours_per_project(hours),
        ]
    )


def format_lines(hours: Hours) -> str:
    output = ["Data from csv file"]
    for entry in hours.entries:
        if entry.skip():
            output.append(f"{entry.line}: empty row")
            continue
        output.append(
            f"{entry.line}: "
            f"{entry.started} ({entry.row.date_cell}), "
            f"{entry.seconds} ({entry.row.hours_cell}), "
            f"'{entry.ticket}', "
            f"'{entry.description}'"
        )
    return "\n".join(output)


def format_hours_per_day(hours: Hours) -> str:
    output = ["Hours per date"]
    for d, h in hours.per_day().items():
        hours_str = f"{h}"
        if hours_str == "0.0":
            hours_str = "-"
        output.append(f"{d}: {hours_str}")
    return "\n".join(output)


def format_hours_per_ticket(hours: Hours) -> str:
    output = ["Hours per ticket"]
    for ticket, h in hours.per_ticket().items():
        output.append(f"{ticket}: {h}")
    return "\n".join(output)


def format_hours_per_project(hours: Hours) -> str:
    output = ["Hours per project"]
    for project, h in hours.per_project().items():
        output.append(f"{project}: {h}")
    return "\n".join(output)
