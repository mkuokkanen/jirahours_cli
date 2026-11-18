"""The shared specification every Timesheet implementation is held to.

The ABC barely constrains anything, so this suite is the real contract. Add an
implementation to IMPLEMENTATIONS and either it agrees here or it fails.

Deliberately loose about wording: each implementation validates the file its
own native way, so the exact error text and the error subclass are its own
business. What is pinned is the machine-readable output, worklogs and totals,
and that an invalid file is rejected with a TimesheetError pointing at the
offending line.
"""

from collections.abc import Callable
from datetime import date
from pathlib import Path

import pytest

from jirahours.timesheet.base import Timesheet, TimesheetError
from jirahours.timesheet.stdlib.timesheet import StdlibTimesheet

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
# TOTALS - what the user checks before submitting, pinned exactly
#


@pytest.fixture
def unordered_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "unordered.csv"
    csv_file.write_text(
        "3.1.2020;8;XY-9;Other work\n"
        "1.1.2020;6;ABC-1;Work\n"
        "1.1.2020;1,5;ABC-2;More work\n",
        encoding="utf-8",
    )
    return csv_file


@pytest.fixture
def mixed_case_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "mixed_case.csv"
    csv_file.write_text(
        "1.1.2020;6;abc-1;Work\n2.1.2020;2;ABC-2;More work\n", encoding="utf-8"
    )
    return csv_file


def test_hours_per_day_cover_every_date_in_range(
    implementation: TimesheetFactory,
) -> None:
    per_day = implementation(Path("tests/csv_files/ok.csv")).hours_per_day()
    assert list(per_day) == [date(2024, 1, d) for d in range(2, 14)]
    assert per_day[date(2024, 1, 2)] == 2.5
    assert per_day[date(2024, 1, 13)] == 8.0
    assert sum(per_day.values()) == 10.5


def test_hours_per_day_sum_rows_and_are_ordered_by_date(
    implementation: TimesheetFactory, unordered_csv: Path
) -> None:
    assert list(implementation(unordered_csv).hours_per_day().items()) == [
        (date(2020, 1, 1), 7.5),
        (date(2020, 1, 2), 0.0),
        (date(2020, 1, 3), 8.0),
    ]


def test_hours_per_ticket(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/ok.csv"))
    assert sheet.hours_per_ticket() == {"TICKET-123": 2.5, "TICKET-321": 8.0}


def test_hours_per_ticket_are_ordered_by_ticket(
    implementation: TimesheetFactory, unordered_csv: Path
) -> None:
    assert list(implementation(unordered_csv).hours_per_ticket().items()) == [
        ("ABC-1", 6.0),
        ("ABC-2", 1.5),
        ("XY-9", 8.0),
    ]


def test_hours_per_ticket_keep_the_spelling_of_the_file(
    implementation: TimesheetFactory, mixed_case_csv: Path
) -> None:
    per_ticket = implementation(mixed_case_csv).hours_per_ticket()
    assert per_ticket == {"ABC-2": 2.0, "abc-1": 6.0}


def test_hours_per_project(implementation: TimesheetFactory) -> None:
    sheet = implementation(Path("tests/csv_files/ok.csv"))
    assert sheet.hours_per_project() == {"TICKET": 10.5}


def test_hours_per_project_sum_tickets_and_are_ordered_by_project(
    implementation: TimesheetFactory, unordered_csv: Path
) -> None:
    assert list(implementation(unordered_csv).hours_per_project().items()) == [
        ("ABC", 7.5),
        ("XY", 8.0),
    ]


def test_hours_per_project_grouping_is_case_insensitive(
    implementation: TimesheetFactory, mixed_case_csv: Path
) -> None:
    assert implementation(mixed_case_csv).hours_per_project() == {"ABC": 8.0}


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
