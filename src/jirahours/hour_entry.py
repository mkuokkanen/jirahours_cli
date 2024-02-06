import re
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from jirahours.errors import CsvError


class HourEntry:

    def __init__(
        self,
        line: int,
        date_cell: str,
        hours_cell: str,
        ticket_cell: str,
        description_cell: str,
        date_input_format: str = "%d.%m.%Y",
    ):
        # csv row number
        self.line = line
        # csv cell data
        self.date_cell: str = date_cell.strip()
        self.hours_cell: str = hours_cell.strip()
        self.ticket_cell: str = ticket_cell.strip()
        self.description_cell: str = description_cell.strip()
        # config
        self._date_input_format = date_input_format
        # validate input data automatically
        self._validate()

    def skip(self) -> bool:
        return self.date_cell == ""

    @property
    def started(self) -> str:
        # Convert the input date string to a datetime object
        try:
            naive_date = datetime.strptime(self.date_cell, self._date_input_format)
        except Exception as e:
            raise CsvError(self.line, str(e))
        # add time part
        time_component = timedelta(hours=5, minutes=0, seconds=0, milliseconds=0)
        naive_datetime = naive_date + time_component
        # from local timezone to utc timezone
        datetime_utc = naive_datetime.astimezone().astimezone(tz=ZoneInfo("utc"))
        # CHECK not too distant past
        if datetime_utc < datetime.now(UTC) - timedelta(days=60):
            raise CsvError(
                self.line, f"date value '{self.date_cell}' is more than 60 days old"
            )
        # CHECK not in future
        if datetime_utc > datetime.now(UTC):
            raise CsvError(self.line, f"date value '{self.date_cell}' is in future")
        return datetime_utc.isoformat(timespec="milliseconds").replace(
            "+00:00", "+0000"
        )

    @property
    def seconds(self) -> int:
        hours_cell = self.hours_cell.strip()
        replaced_hours_str = hours_cell.replace(",", ".")
        try:
            hours = float(replaced_hours_str)
        except Exception as e:
            raise CsvError(self.line, str(e))
        seconds = int(hours * 3600)
        # CHECK not less than 30 minutes
        if seconds < 0.5 * 60 * 60:
            raise CsvError(
                self.line, f"hour value '{self.hours_cell}' is less than 30 minutes"
            )
        # CHECK not more than 12 hours
        if seconds > 12 * 60 * 60:
            raise CsvError(
                self.line, f"hour value '{self.hours_cell}' is more than 12 hours"
            )
        return seconds

    @property
    def ticket(self) -> str:
        ticket_cell = self.ticket_cell.strip()
        # CHECK correct format
        pattern = re.compile(r"^[A-Za-z]+-\d+$")
        if not pattern.match(ticket_cell):
            raise CsvError(
                self.line,
                f"ticket value '{self.ticket_cell}' is not in correct format",
            )
        return ticket_cell

    @property
    def description(self) -> str:
        description_cell = self.description_cell.strip()
        # CHECK not empty
        if len(description_cell) == 0:
            raise CsvError(self.line, f"description is missing")
        return description_cell

    def _validate(self) -> None:
        """Validate just calls all getters, which contain checks."""
        if self.skip():
            return
        _ = self.started
        _ = self.seconds
        _ = self.ticket
        _ = self.description