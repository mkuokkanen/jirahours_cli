"""The timesheet contract every implementation shares.

Implementations live in the subpackages next to this file.
One subpackage per implementation, each subclassing Timesheet.

The CSV format in the README is the specification implementations must support.
Tests should test that the implementation reads the CSV file correctly.

This module must not import any implementation, so the dependency runs one
way only.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from click import ClickException


@dataclass(frozen=True)
class Worklog:
    """One unit of work, in the form JiraBackend needs it.

    Shared by every implementation, so keep it to what the submission uses.
    """

    line: int
    started: str
    seconds: int
    ticket: str
    description: str


class Timesheet(ABC):
    """A parsed and validated timesheet, as the application needs it."""

    @abstractmethod
    def summary(self) -> str:
        """Human-readable summary of the file, for the user to check."""

    @abstractmethod
    def worklogs(self) -> Sequence[Worklog]:
        """The work to submit, empty rows already dropped."""


class TimesheetError(ClickException):
    """Raised when a file is not a valid timesheet.

    A ClickException, so the CLI prints it without a traceback.
    Implementations can create their own subclasses.
    line is the offending source line, if known.
    """

    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line
