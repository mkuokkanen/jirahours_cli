from click import ClickException


class TimesheetError(ClickException):
    """A source could not be read as a timesheet.

    Part of the contract: an implementation that meets a file it cannot accept
    must say so by raising this, not by skipping the row or guessing. It
    subclasses ClickException so that the CLI prints it plainly instead of a
    traceback.

    Each implementation raises its own subclass and words the message however
    suits the way it validates. The line number is kept as structured data so
    that a caller can rely on it without parsing the message.
    """

    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line
