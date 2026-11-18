"""The timesheet contract every implementation shares.

The CSV format in the README is the specification implementations must support.
Tests should test that the implementation reads the CSV file correctly.

This module must not import any implementation, so the dependency runs one
way only.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from click import ClickException


@dataclass(frozen=True)
class Worklog:
    """One unit of work, in the form submission needs it.

    Shared by every implementation, so keep it to what the submission uses.
    """

    line: int
    started: str
    seconds: int
    ticket: str
    description: str


class Timesheet(ABC):
    """A parsed and validated timesheet, as the application needs it.

    Totals are in hours, summed over the non-empty lines, ordered by key.
    """

    @abstractmethod
    def worklogs(self) -> Sequence[Worklog]:
        """The work to submit, empty rows already dropped."""

    @abstractmethod
    def hours_per_day(self) -> Mapping[date, float]:
        """Every date from the first to the last, 0.0 for dates without work."""

    @abstractmethod
    def hours_per_ticket(self) -> Mapping[str, float]:
        """Tickets as written in the file."""

    @abstractmethod
    def hours_per_project(self) -> Mapping[str, float]:
        """Projects are ticket prefixes, upper cased, so 'abc-1' joins 'ABC-2'."""


class TimesheetError(ClickException):
    """Raised when a file is not a valid timesheet.

    A ClickException, so the CLI prints it without a traceback.
    Implementations can create their own subclasses.
    line is the offending source line, if known.
    """

    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line
