from datetime import timedelta

from jirahours.hour_entries import HourEntries


def rows(data: HourEntries) -> str:
    output = ["Data from csv file"]
    for each in data.entries:
        if each.skip():
            output.append(f"{each.line}: empty row")
            continue
        output.append(
            f"{each.line}: "
            f"{each.started} ({each.date_cell}), "
            f"{each.seconds} ({each.hours_cell}), "
            f"'{each.ticket}', "
            f"'{each.description}'"
        )
    return "\n".join(output)


def hours_per_day(data: HourEntries) -> str:
    output = ["Hours per date"]
    d = data.min_date()
    while d <= data.max_date():
        output.append(f"{d}: {data.hours_per_date(d)}")
        d += timedelta(days=1)
    return "\n".join(output)


def hours_per_ticket(data: HourEntries) -> str:
    output = ["Hours per ticket"]
    for t in data.tickets():
        output.append(f"{t}: {data.hours_per_ticket(t)}")
    return "\n".join(output)
