from jirahours.timesheet import TimesheetError


class CsvError(TimesheetError):
    """This implementation's wording for a rejected row.

    Reading row by row means there is always exactly one offending line to
    point at, so it always reports one.
    """

    def __init__(self, line: int, msg: str):
        super().__init__(f"csv line {line}: " + msg, line=line)
