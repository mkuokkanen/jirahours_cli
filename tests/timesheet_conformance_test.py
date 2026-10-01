"""The shared specification every Timesheet implementation is held to.

The ABC barely constrains anything, so this suite is the real contract. Add an
implementation to IMPLEMENTATIONS and either it agrees here or it fails.

Deliberately loose about wording: each implementation validates the file its
own native way, so the exact error text, the error subclass and the exact
rendering are all its own business. What is pinned is the machine-readable
output, and that an invalid file is rejected with a TimesheetError pointing at
the offending line.
"""

from collections.abc import Callable
from pathlib import Path

import pytest

from jirahours.timesheet import Timesheet, TimesheetError
from jirahours.timesheet.implementations import StdlibTimesheet

TimesheetFactory = Callable[[Path], Timesheet]

IMPLEMENTATIONS: list[TimesheetFactory] = [
    StdlibTimesheet,
]


@pytest.fixture(params=IMPLEMENTATIONS)
def implementation(request: pytest.FixtureRequest) -> TimesheetFactory:
    factory: TimesheetFactory = request.param
    return factory


#
# WORKLOGS - the machine readable output, pinned exactly
#


def test_worklogs_skip_empty_rows(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/ok.csv"))
    # line 2 of the file is empty and must not become a worklog
    assert [w.line for w in sheet.worklogs()] == [1, 3]


def test_worklogs_are_parsed(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/ok.csv"))
    first, third = sheet.worklogs()
    # quoted row, comma decimal in hours, comma inside the quoted description
    assert first.started == "2024-01-02T03:00:00.000+0000"
    assert first.seconds == 9000
    assert first.ticket == "TICKET-123"
    assert first.description == "Some description, with comma"
    # unquoted row, single digit day, padded cells, emoji
    assert third.started == "2024-01-13T03:00:00.000+0000"
    assert third.seconds == 28800
    assert third.ticket == "TICKET-321"
    assert third.description == "Other description with emoji without quotes 👍"


def test_leading_bom_is_ignored(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/ok_bom.csv"))
    assert [w.ticket for w in sheet.worklogs()] == ["TICKET-123"]
    assert [w.seconds for w in sheet.worklogs()] == [9000]


#
# SUMMARY - has to say something useful, wording is the implementation's own
#


def test_summary_mentions_every_ticket(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/ok.csv"))
    summary = sheet.summary()
    assert "TICKET-123" in summary
    assert "TICKET-321" in summary


def test_summary_of_a_single_row_file(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/ok_bom.csv"))
    summary = sheet.summary()
    assert "TICKET-123" in summary
    assert "2.5" in summary


#
# VALIDATION - rejection is required, the message wording is not
#


def test_extra_column_is_rejected(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/error_extra_column.csv"))
    with pytest.raises(TimesheetError) as exc_info:
        _ = sheet.worklogs()
    # line 2 is the row with the extra column, however the message words it
    assert exc_info.value.line == 2


def test_partly_filled_row_is_rejected(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/error_partly_filled.csv"))
    with pytest.raises(TimesheetError) as exc_info:
        _ = sheet.worklogs()
    assert exc_info.value.line == 1
