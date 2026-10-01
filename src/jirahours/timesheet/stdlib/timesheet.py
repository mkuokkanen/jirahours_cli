import csv
from collections.abc import Sequence
from functools import cached_property
from pathlib import Path

from jirahours.timesheet.base import Timesheet, Worklog
from jirahours.timesheet.stdlib import display
from jirahours.timesheet.stdlib.model import Hours
from jirahours.timesheet.stdlib.parse import to_hours


class StdlibTimesheet(Timesheet):
    """Reads and validates the CSV file with the standard library's csv module.

    Row at a time, plain Python checks, no dependencies.
    """

    def __init__(
        self,
        path: Path,
        delimiter: str = ";",
        quotechar: str = '"',
    ) -> None:
        self._path = path
        self._delimiter = delimiter
        self._quotechar = quotechar

    def summary(self) -> str:
        return display.summary(self._hours)

    def worklogs(self) -> Sequence[Worklog]:
        return self._hours.worklogs()

    @cached_property
    def _hours(self) -> Hours:
        """Read and validate the file once, on first use.

        utf-8-sig is used to drop the BOM that some tools insert at the
        beginning of the file.
        """
        # with block so that the file is closed in case of error
        with self._path.open(encoding="utf-8-sig") as csv_file:
            return to_hours(
                csv.reader(
                    csv_file,
                    delimiter=self._delimiter,
                    quotechar=self._quotechar,
                )
            )
