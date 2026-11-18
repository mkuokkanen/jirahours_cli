"""The contract for where worklogs get sent.

The contract lets the application send worklogs without knowing where they
go, and lets the submit loop be tested against a fake, without the network.

tests/submitter/conformance_test.py holds every implementation to the contract.

This module must not import any implementation, so the dependency runs one
way only.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from jirahours.timesheet.base import Worklog


@dataclass(frozen=True)
class Submitted:
    """What came back from sending one worklog, for the user to check."""

    line: int
    ok: bool
    message: str


class Submitter(ABC):
    """Somewhere worklogs can be sent."""

    @abstractmethod
    def add_worklog(self, worklog: Worklog) -> Submitted:
        """Send one worklog and report the outcome.

        Never raises for a failed send: report it with ok=False instead, so
        that the caller can stop and tell the user what was sent.
        """
