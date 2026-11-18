"""The console rendering, fed a timesheet holding literal data."""

from collections.abc import Mapping, Sequence
from datetime import date

import pytest

from jirahours.timesheet.base import Timesheet, Worklog
from jirahours.visualizer import console


class FixedTimesheet(Timesheet):
    def __init__(
        self,
        worklogs: Sequence[Worklog],
        hours_per_day: Mapping[date, float],
        hours_per_ticket: Mapping[str, float],
        hours_per_project: Mapping[str, float],
    ) -> None:
        self._worklogs = worklogs
        self._per_day = hours_per_day
        self._per_ticket = hours_per_ticket
        self._per_project = hours_per_project

    def worklogs(self) -> Sequence[Worklog]:
        return self._worklogs

    def hours_per_day(self) -> Mapping[date, float]:
        return self._per_day

    def hours_per_ticket(self) -> Mapping[str, float]:
        return self._per_ticket

    def hours_per_project(self) -> Mapping[str, float]:
        return self._per_project


def _worklog(line: int, day: int, hours: int, ticket: str, description: str) -> Worklog:
    return Worklog(
        line=line,
        started=f"2024-05-{day:02}T02:00:00.000+0000",
        seconds=hours * 3600,
        ticket=ticket,
        description=description,
    )


@pytest.fixture
def empty_data() -> Timesheet:
    return FixedTimesheet(
        worklogs=[], hours_per_day={}, hours_per_ticket={}, hours_per_project={}
    )


@pytest.fixture
def single_entry_data() -> Timesheet:
    return FixedTimesheet(
        worklogs=[_worklog(1, 1, 1, "JKL-123", "Sample Issue")],
        hours_per_day={date(2024, 5, 1): 1.0},
        hours_per_ticket={"JKL-123": 1.0},
        hours_per_project={"JKL": 1.0},
    )


@pytest.fixture
def multiple_entries_data() -> Timesheet:
    return FixedTimesheet(
        worklogs=[
            _worklog(1, 1, 1, "JKL-123", "Sample Issue"),
            _worklog(2, 3, 2, "ABC-456", "Another Issue"),
            _worklog(3, 4, 2, "ABC-456", "Another Issue"),
        ],
        hours_per_day={
            date(2024, 5, 1): 1.0,
            date(2024, 5, 2): 0.0,
            date(2024, 5, 3): 2.0,
            date(2024, 5, 4): 2.0,
        },
        hours_per_ticket={"ABC-456": 4.0, "JKL-123": 1.0},
        hours_per_project={"ABC": 4.0, "JKL": 1.0},
    )


#
# FORMAT_WORKLOGS
#


def test_format_worklogs_empty_data(empty_data: Timesheet) -> None:
    assert console.format_worklogs(empty_data) == "Data from csv file"


def test_format_worklogs_with_single_entry_data(single_entry_data: Timesheet) -> None:
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000, 3600, 'JKL-123', 'Sample Issue'
    """.strip()
    assert console.format_worklogs(single_entry_data) == expected_output


def test_format_worklogs_with_multiple_entries_data(
    multiple_entries_data: Timesheet,
) -> None:
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000, 3600, 'JKL-123', 'Sample Issue'
2: 2024-05-03T02:00:00.000+0000, 7200, 'ABC-456', 'Another Issue'
3: 2024-05-04T02:00:00.000+0000, 7200, 'ABC-456', 'Another Issue'
    """.strip()
    assert console.format_worklogs(multiple_entries_data) == expected_output


#
# FORMAT_HOURS_PER_DAY
#


def test_format_hours_per_day_empty_data(empty_data: Timesheet) -> None:
    assert console.format_hours_per_day(empty_data) == "Hours per date"


def test_format_hours_per_day_with_single_entry_data(
    single_entry_data: Timesheet,
) -> None:
    expected_output = """
Hours per date
2024-05-01: 1.0
    """.strip()
    assert console.format_hours_per_day(single_entry_data) == expected_output


def test_format_hours_per_day_with_multiple_entries_data(
    multiple_entries_data: Timesheet,
) -> None:
    expected_output = """
Hours per date
2024-05-01: 1.0
2024-05-02: -
2024-05-03: 2.0
2024-05-04: 2.0
    """.strip()
    assert console.format_hours_per_day(multiple_entries_data) == expected_output


#
# FORMAT_HOURS_PER_TICKET
#


def test_format_hours_per_ticket_empty_data(empty_data: Timesheet) -> None:
    assert console.format_hours_per_ticket(empty_data) == "Hours per ticket"


def test_format_hours_per_ticket_with_single_entry_data(
    single_entry_data: Timesheet,
) -> None:
    expected_output = """
Hours per ticket
JKL-123: 1.0
    """.strip()
    assert console.format_hours_per_ticket(single_entry_data) == expected_output


def test_format_hours_per_ticket_with_multiple_entries_data(
    multiple_entries_data: Timesheet,
) -> None:
    expected_output = """
Hours per ticket
ABC-456: 4.0
JKL-123: 1.0
    """.strip()
    assert console.format_hours_per_ticket(multiple_entries_data) == expected_output


#
# FORMAT_HOURS_PER_PROJECT
#


def test_format_hours_per_project_empty_data(empty_data: Timesheet) -> None:
    assert console.format_hours_per_project(empty_data) == "Hours per project"


def test_format_hours_per_project_with_single_entry_data(
    single_entry_data: Timesheet,
) -> None:
    expected_output = """
Hours per project
JKL: 1.0
    """.strip()
    assert console.format_hours_per_project(single_entry_data) == expected_output


def test_format_hours_per_project_with_multiple_entries_data(
    multiple_entries_data: Timesheet,
) -> None:
    expected_output = """
Hours per project
ABC: 4.0
JKL: 1.0
    """.strip()
    assert console.format_hours_per_project(multiple_entries_data) == expected_output


#
# SUMMARY
#


def test_summary_joins_every_section(single_entry_data: Timesheet) -> None:
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000, 3600, 'JKL-123', 'Sample Issue'

Hours per date
2024-05-01: 1.0

Hours per ticket
JKL-123: 1.0

Hours per project
JKL: 1.0
    """.strip()
    assert console.summary(single_entry_data) == expected_output


def test_summary_of_empty_data(empty_data: Timesheet) -> None:
    expected_output = """
Data from csv file

Hours per date

Hours per ticket

Hours per project
    """.strip()
    assert console.summary(empty_data) == expected_output
