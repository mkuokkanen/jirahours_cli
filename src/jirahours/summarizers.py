from datetime import timedelta

from jirahours.model import Hours


def rows(data: Hours) -> str:
    output = ["Data from csv file"]
    for each in data.entries:
        if each.skip():
            output.append(f"{each.line}: empty row")
            continue
        output.append(
            f"{each.line}: "
            f"{each.started} ({each.row.date_cell}), "
            f"{each.seconds} ({each.row.hours_cell}), "
            f"'{each.ticket}', "
            f"'{each.description}'"
        )
    return "\n".join(output)


def hours_per_day(data: Hours) -> str:
    output = ["Hours per date"]
    if data.entries:
        d = data.min_date()
        while d <= data.max_date():
            hours_str = f"{data.hours_per_date(d)}"
            if hours_str == "0.0":
                hours_str = "-"
            output.append(f"{d}: {hours_str}")
            d += timedelta(days=1)
    return "\n".join(output)


def hours_per_ticket(data: Hours) -> str:
    output = ["Hours per ticket"]
    for t in data.tickets():
        output.append(f"{t}: {data.hours_per_ticket(t)}")
    return "\n".join(output)
