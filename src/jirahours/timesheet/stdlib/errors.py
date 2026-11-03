from jirahours.timesheet.base import TimesheetError


class CsvError(TimesheetError):
    """This implementation's error for a rejected row."""

    def __init__(self, line: int, msg: str):
        super().__init__(f"csv line {line}: " + msg, line=line)
