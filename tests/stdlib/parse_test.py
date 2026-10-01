"""This implementation's shape validation, fed literal cells."""

from datetime import date

import pytest

from jirahours.timesheet.implementations.stdlib._errors import CsvError
from jirahours.timesheet.implementations.stdlib._parse import to_hours


def test_empty_source() -> None:
    hours = to_hours([])
    assert hours.entries == []
    assert hours.per_day() == {}
    assert hours.per_ticket() == {}
    assert hours.per_project() == {}


def test_all_empty_row_is_allowed() -> None:
    hours = to_hours([["", "", "", ""], ["  ", "", "\t", " "]])
    assert [e.skip() for e in hours.entries] == [True, True]
    assert hours.per_day() == {}
    assert hours.worklogs() == []


def test_too_few_columns() -> None:
    with pytest.raises(CsvError) as exc_info:
        to_hours([["1.1.2020", "6", "ABC-1"]])
    assert str(exc_info.value) == "csv line 1: found 3 columns instead of expected 4"


def test_too_many_columns() -> None:
    with pytest.raises(CsvError) as exc_info:
        to_hours([["1.1.2020", "6", "ABC-1", "Work", "extra"]])
    assert str(exc_info.value) == "csv line 1: found 5 columns instead of expected 4"


def test_partly_filled_row_reports_its_line() -> None:
    with pytest.raises(CsvError) as exc_info:
        to_hours(
            [
                ["1.1.2020", "6", "ABC-1", "Work"],
                ["2.1.2020", " ", "ABC-1", "Work"],
            ]
        )
    assert str(exc_info.value) == "csv line 2: row only partly filled"


def test_aggregations_sum_across_rows() -> None:
    hours = to_hours(
        [
            ["1.1.2020", "6", "ABC-1", "Work"],
            ["1.1.2020", "1,5", "ABC-2", "More work"],
            ["", "", "", ""],
            ["3.1.2020", "8", "XY-9", "Other work"],
        ]
    )
    assert hours.per_day() == {
        date(2020, 1, 1): 7.5,
        date(2020, 1, 2): 0.0,
        date(2020, 1, 3): 8.0,
    }
    assert hours.per_ticket() == {"ABC-1": 6.0, "ABC-2": 1.5, "XY-9": 8.0}
    assert hours.per_project() == {"ABC": 7.5, "XY": 8.0}


def test_project_grouping_is_case_insensitive() -> None:
    hours = to_hours(
        [
            ["1.1.2020", "6", "abc-1", "Work"],
            ["2.1.2020", "2", "ABC-2", "More work"],
        ]
    )
    # tickets keep their original spelling, projects are normalised
    assert hours.per_ticket() == {"ABC-2": 2.0, "abc-1": 6.0}
    assert hours.per_project() == {"ABC": 8.0}


def test_worklogs_drop_empty_rows_and_keep_line_numbers() -> None:
    hours = to_hours(
        [
            ["", "", "", ""],
            ["2.1.2020", "6", "ABC-1", "Work"],
        ]
    )
    worklogs = hours.worklogs()
    assert [w.line for w in worklogs] == [2]
    assert worklogs[0].seconds == 6 * 60 * 60
    assert worklogs[0].started == "2020-01-02T03:00:00.000+0000"
