import re
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from jirahours.timesheet import Worklog
from jirahours.timesheet.implementations.stdlib._errors import CsvError


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
            return date.strptime(self.row.date_cell, self._date_input_format)
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
    def project(self) -> str:
        """Ticket prefix, upper cased so that 'abc-1' and 'ABC-2' group together."""
        return self.ticket.split("-", 1)[0].upper()

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
    """All entries in data set and the aggregations over them.

    Private to this implementation. The aggregations feed its own rendering,
    so nothing outside needs them.
    """

    def __init__(self, entries: list[Entry]) -> None:
        self.entries: list[Entry] = entries

    @property
    def valid_entries(self) -> list[Entry]:
        return [e for e in self.entries if not e.skip()]

    def worklogs(self) -> list[Worklog]:
        """Convert to the format the application shares, empty rows dropped."""
        return [
            Worklog(
                line=e.line,
                started=e.started,
                seconds=e.seconds,
                ticket=e.ticket,
                description=e.description,
            )
            for e in self.valid_entries
        ]

    def per_day(self, fill_gaps: bool = True) -> dict[date, float]:
        """Hours per date, ordered by date.

        With fill_gaps, dates inside the range that have no hours are included
        as 0.0, so a caller can print a continuous calendar without knowing the
        first and last date itself.
        """
        seconds: dict[date, int] = {}
        for e in self.valid_entries:
            seconds[e.date] = seconds.get(e.date, 0) + e.seconds
        if not seconds:
            return {}
        if not fill_gaps:
            return {d: s / 60 / 60 for d, s in sorted(seconds.items())}
        filled: dict[date, float] = {}
        d = min(seconds)
        last = max(seconds)
        while d <= last:
            filled[d] = seconds.get(d, 0) / 60 / 60
            d += timedelta(days=1)
        return filled

    def per_ticket(self) -> dict[str, float]:
        """Hours per ticket, ordered by ticket."""
        return self._totals(lambda e: e.ticket)

    def per_project(self) -> dict[str, float]:
        """Hours per project, ordered by project."""
        return self._totals(lambda e: e.project)

    def _totals(self, key: Callable[[Entry], str]) -> dict[str, float]:
        """Sum seconds per key, then convert once, to avoid float drift."""
        seconds: dict[str, int] = {}
        for e in self.valid_entries:
            k = key(e)
            seconds[k] = seconds.get(k, 0) + e.seconds
        return {k: s / 60 / 60 for k, s in sorted(seconds.items())}
