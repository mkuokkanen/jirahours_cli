import re
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from jirahours.exceptions import CsvError


class Row:
    """Container for CSV row data."""

    def __init__(
        self,
        line: int,
        date_cell: str,
        hours_cell: str,
        ticket_cell: str,
        description_cell: str,
    ):
        # csv row number
        self.line = line
        # csv cell data
        self.date_cell: str = date_cell.strip()
        self.hours_cell: str = hours_cell.strip()
        self.ticket_cell: str = ticket_cell.strip()
        self.description_cell: str = description_cell.strip()


class Entry:
    """Row data interpreted for future processing."""

    def __init__(self, row: Row):
        self.row = row
        # config
        self._date_input_format = "%d.%m.%Y"
        self._time: time = time(hour=5, minute=0, second=0)
        self._timezone: ZoneInfo = ZoneInfo("Europe/Helsinki")
        # trigger validation
        self.validate()

    def skip(self) -> bool:
        return self.row.date_cell == ""

    @property
    def line(self) -> int:
        return self.row.line

    @property
    def date(self) -> date:
        try:
            return datetime.strptime(self.row.date_cell, self._date_input_format).date()
        except Exception as e:
            raise CsvError(self.row.line, str(e))

    @property
    def started(self) -> str:
        # date from local tz to utc tz
        datetime_hki = datetime.combine(self.date, self._time, tzinfo=self._timezone)
        datetime_utc = datetime_hki.astimezone(tz=ZoneInfo("UTC"))
        # mangle to target format
        datetime_str = datetime_utc.isoformat(timespec="milliseconds")
        datetime_str = datetime_str.replace("+00:00", "+0000")
        return datetime_str

    @property
    def seconds(self) -> int:
        hours_cell = self.row.hours_cell.strip()
        replaced_hours_str = hours_cell.replace(",", ".")
        try:
            hours = float(replaced_hours_str)
        except Exception as e:
            raise CsvError(self.row.line, str(e))
        seconds = int(hours * 3600)
        # CHECK not less than 30 minutes
        if seconds < 0.5 * 60 * 60:
            raise CsvError(
                self.row.line,
                f"hour value '{self.row.hours_cell}' is less than 30 minutes",
            )
        # CHECK not more than 12 hours
        if seconds > 12 * 60 * 60:
            raise CsvError(
                self.row.line,
                f"hour value '{self.row.hours_cell}' is more than 12 hours",
            )
        return seconds

    @property
    def ticket(self) -> str:
        ticket_cell = self.row.ticket_cell.strip()
        # CHECK correct format
        pattern = re.compile(r"^[A-Za-z]+-\d+$")
        if not pattern.match(ticket_cell):
            raise CsvError(
                self.row.line,
                f"ticket value '{self.row.ticket_cell}' is not in correct format",
            )
        return ticket_cell

    @property
    def description(self) -> str:
        description_cell = self.row.description_cell.strip()
        # CHECK not empty
        if len(description_cell) == 0:
            raise CsvError(self.row.line, f"description is missing")
        return description_cell

    def validate(self) -> None:
        """Validate just calls all getters, which contain checks."""
        if self.skip():
            return
        _ = self.started
        _ = self.seconds
        _ = self.ticket
        _ = self.description


class Hours:
    """All entries in data set and supporting functions."""

    def __init__(self, entries: list[Entry]) -> None:
        self.entries: list[Entry] = entries

    @property
    def valid_entries(self) -> list[Entry]:
        return [e for e in self.entries if not e.skip()]

    def min_date(self) -> date:
        dates = [e.date for e in self.valid_entries]
        return min(dates)

    def max_date(self) -> date:
        dates = [e.date for e in self.valid_entries]
        return max(dates)

    def hours_per_date(self, d: date) -> float:
        seconds = sum([e.seconds for e in self.valid_entries if e.date == d])
        return seconds / 60 / 60

    def tickets(self) -> list[str]:
        t = list(set([e.ticket for e in self.valid_entries]))
        t.sort()
        return t

    def hours_per_ticket(self, ticket: str) -> float:
        seconds = sum([e.seconds for e in self.valid_entries if e.ticket == ticket])
        return seconds / 60 / 60
