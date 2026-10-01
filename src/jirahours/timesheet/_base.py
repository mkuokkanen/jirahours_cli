from abc import ABC, abstractmethod
from collections.abc import Sequence

from jirahours.timesheet._worklog import Worklog


class Timesheet(ABC):
    """What the application needs from a timesheet, and nothing else.

    An implementation reads the CSV file, decides for itself how to validate it
    and how to present it, and answers these two questions. Reading, validating
    and rendering are all free to be done the way the chosen library does them
    best, which is what makes the implementations worth comparing.

    The shared specification is not this class, which barely constrains
    anything: it is the CSV format in the README, and the conformance test
    suite that every implementation is held to.
    """

    @abstractmethod
    def summary(self) -> str:
        """Human-readable summary of the file, for the user to check."""

    @abstractmethod
    def worklogs(self) -> Sequence[Worklog]:
        """The work to submit, empty rows already dropped."""
