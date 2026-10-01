import csv
from collections.abc import Sequence
from functools import cached_property
from pathlib import Path

from jirahours.timesheet import Timesheet, Worklog
from jirahours.timesheet.implementations.stdlib import _display
from jirahours.timesheet.implementations.stdlib._model import Hours
from jirahours.timesheet.implementations.stdlib._parse import to_hours


class StdlibTimesheet(Timesheet):
    """Reads and validates the CSV file with the standard library's csv module.

    Row at a time, plain Python checks, no dependencies. The baseline the other
    implementations are compared against.
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
        return _display.summary(self._hours)

    def worklogs(self) -> Sequence[Worklog]:
        return self._hours.worklogs()

    @cached_property
    def _hours(self) -> Hours:
        """Read and validate the file once, on first use.

        Parsing happens inside the with block on purpose. Handing the reader
        out of it, so that rows are pulled lazily from somewhere else, leaves
        the file open whenever validation rejects a row part way through.
        """
        # utf-8-sig drops the BOM that spreadsheet exports tend to leave behind
        with self._path.open(encoding="utf-8-sig") as csv_file:
            return to_hours(
                csv.reader(
                    csv_file,
                    delimiter=self._delimiter,
                    quotechar=self._quotechar,
                )
            )
