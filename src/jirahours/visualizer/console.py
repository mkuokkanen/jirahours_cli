"""Shows a timesheet as plain text for the terminal."""

from jirahours.timesheet.base import Timesheet


def summary(t: Timesheet) -> str:
    """Every section, blank line separated."""
    return "\n\n".join(
        [
            format_worklogs(t),
            format_hours_per_day(t),
            format_hours_per_ticket(t),
            format_hours_per_project(t),
        ]
    )


def format_worklogs(t: Timesheet) -> str:
    output = ["Data from csv file"]
    for w in t.worklogs():
        output.append(
            f"{w.line}: {w.started}, {w.seconds}, '{w.ticket}', '{w.description}'"
        )
    return "\n".join(output)


def format_hours_per_day(t: Timesheet) -> str:
    output = ["Hours per date"]
    for d, h in t.hours_per_day().items():
        hours_str = f"{h}"
        if hours_str == "0.0":
            hours_str = "-"
        output.append(f"{d}: {hours_str}")
    return "\n".join(output)


def format_hours_per_ticket(t: Timesheet) -> str:
    output = ["Hours per ticket"]
    for ticket, h in t.hours_per_ticket().items():
        output.append(f"{ticket}: {h}")
    return "\n".join(output)


def format_hours_per_project(t: Timesheet) -> str:
    output = ["Hours per project"]
    for project, h in t.hours_per_project().items():
        output.append(f"{project}: {h}")
    return "\n".join(output)
