"""This implementation's rendering, fed literal cells."""

import pytest

from jirahours.timesheet.implementations.stdlib import _display
from jirahours.timesheet.implementations.stdlib._model import Hours
from jirahours.timesheet.implementations.stdlib._parse import to_hours


@pytest.fixture
def empty_data() -> Hours:
    return to_hours([])


@pytest.fixture
def single_entry_data() -> Hours:
    return to_hours([["01.05.2024", "1", "JKL-123", "Sample Issue"]])


@pytest.fixture
def multiple_entries_data() -> Hours:
    return to_hours(
        [
            ["01.05.2024", "1", "JKL-123", "Sample Issue"],
            ["03.05.2024", "2", "ABC-456", "Another Issue"],
            ["04.05.2024", "2", "ABC-456", "Another Issue"],
        ]
    )


#
# FORMAT_LINES
#


def test_format_lines_empty_data(empty_data: Hours) -> None:
    assert _display.format_lines(empty_data) == "Data from csv file"


def test_format_lines_with_single_entry_data(single_entry_data: Hours) -> None:
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000 (01.05.2024), 3600 (1), 'JKL-123', 'Sample Issue'
    """.strip()
    assert _display.format_lines(single_entry_data) == expected_output


def test_format_lines_with_multiple_entries_data(multiple_entries_data: Hours) -> None:
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000 (01.05.2024), 3600 (1), 'JKL-123', 'Sample Issue'
2: 2024-05-03T02:00:00.000+0000 (03.05.2024), 7200 (2), 'ABC-456', 'Another Issue'
3: 2024-05-04T02:00:00.000+0000 (04.05.2024), 7200 (2), 'ABC-456', 'Another Issue'
    """.strip()
    assert _display.format_lines(multiple_entries_data) == expected_output


def test_format_lines_marks_empty_rows() -> None:
    data = to_hours(
        [
            ["01.05.2024", "1", "JKL-123", "Sample Issue"],
            ["", "", "", ""],
        ]
    )
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000 (01.05.2024), 3600 (1), 'JKL-123', 'Sample Issue'
2: empty row
    """.strip()
    assert _display.format_lines(data) == expected_output


#
# FORMAT_HOURS_PER_DAY
#


def test_format_hours_per_day_empty_data(empty_data: Hours) -> None:
    assert _display.format_hours_per_day(empty_data) == "Hours per date"


def test_format_hours_per_day_with_single_entry_data(single_entry_data: Hours) -> None:
    expected_output = """
Hours per date
2024-05-01: 1.0
    """.strip()
    assert _display.format_hours_per_day(single_entry_data) == expected_output


def test_format_hours_per_day_with_multiple_entries_data(
    multiple_entries_data: Hours,
) -> None:
    expected_output = """
Hours per date
2024-05-01: 1.0
2024-05-02: -
2024-05-03: 2.0
2024-05-04: 2.0
    """.strip()
    assert _display.format_hours_per_day(multiple_entries_data) == expected_output


#
# FORMAT_HOURS_PER_TICKET
#


def test_format_hours_per_ticket_empty_data(empty_data: Hours) -> None:
    assert _display.format_hours_per_ticket(empty_data) == "Hours per ticket"


def test_format_hours_per_ticket_with_single_entry_data(
    single_entry_data: Hours,
) -> None:
    expected_output = """
Hours per ticket
JKL-123: 1.0
    """.strip()
    assert _display.format_hours_per_ticket(single_entry_data) == expected_output


def test_format_hours_per_ticket_with_multiple_entries_data(
    multiple_entries_data: Hours,
) -> None:
    expected_output = """
Hours per ticket
ABC-456: 4.0
JKL-123: 1.0
    """.strip()
    assert _display.format_hours_per_ticket(multiple_entries_data) == expected_output


#
# FORMAT_HOURS_PER_PROJECT
#


def test_format_hours_per_project_empty_data(empty_data: Hours) -> None:
    assert _display.format_hours_per_project(empty_data) == "Hours per project"


def test_format_hours_per_project_with_single_entry_data(
    single_entry_data: Hours,
) -> None:
    expected_output = """
Hours per project
JKL: 1.0
    """.strip()
    assert _display.format_hours_per_project(single_entry_data) == expected_output


def test_format_hours_per_project_with_multiple_entries_data(
    multiple_entries_data: Hours,
) -> None:
    expected_output = """
Hours per project
ABC: 4.0
JKL: 1.0
    """.strip()
    assert _display.format_hours_per_project(multiple_entries_data) == expected_output


#
# SUMMARY
#


def test_summary_joins_every_section(single_entry_data: Hours) -> None:
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000 (01.05.2024), 3600 (1), 'JKL-123', 'Sample Issue'

Hours per date
2024-05-01: 1.0

Hours per ticket
JKL-123: 1.0

Hours per project
JKL: 1.0
    """.strip()
    assert _display.summary(single_entry_data) == expected_output


def test_summary_of_empty_data(empty_data: Hours) -> None:
    expected_output = """
Data from csv file

Hours per date

Hours per ticket

Hours per project
    """.strip()
    assert _display.summary(empty_data) == expected_output
