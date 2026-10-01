from dataclasses import dataclass


@dataclass(frozen=True)
class Worklog:
    """One unit of work, in the form JiraBackend needs it.

    This and Timesheet are the only things every implementation shares, so keep
    it to what the submission actually uses. The line number is here so that
    progress can be reported against the source file.
    """

    line: int
    started: str
    seconds: int
    ticket: str
    description: str
