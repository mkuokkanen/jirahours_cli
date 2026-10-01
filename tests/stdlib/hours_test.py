"""Hours is private to this implementation, tested directly as a unit."""

from datetime import date

import pytest

from jirahours.timesheet.implementations.stdlib._model import Entry, Hours, Row


@pytest.fixture
def entry_1() -> Entry:
    return Entry(Row(1, "1.1.2020", "6", "TICKET-1", "Description A"))


@pytest.fixture
def entry_2() -> Entry:
    return Entry(Row(2, "1.1.2020", "7", "TICKET-1", "Description B"))


@pytest.fixture
def entry_3() -> Entry:
    return Entry(Row(3, "", "", "", ""))


@pytest.fixture
def entry_4() -> Entry:
    return Entry(Row(4, "3.1.2020", "8", "OTHER-4", "Description D"))


@pytest.fixture()
def hours(entry_1: Entry, entry_2: Entry, entry_3: Entry, entry_4: Entry) -> Hours:
    entries = [entry_1, entry_2, entry_3, entry_4]
    hour_entries = Hours(entries)
    return hour_entries


def test_length_of_entries(hours: Hours) -> None:
    assert len(hours.entries) == 4


def test_length_of_valid_entries(hours: Hours) -> None:
    assert len(hours.valid_entries) == 3


def test_per_day(hours: Hours) -> None:
    assert hours.per_day() == {
        date(2020, 1, 1): 13.0,
        date(2020, 1, 2): 0.0,
        date(2020, 1, 3): 8.0,
    }


def test_per_day_without_gaps(hours: Hours) -> None:
    assert hours.per_day(fill_gaps=False) == {
        date(2020, 1, 1): 13.0,
        date(2020, 1, 3): 8.0,
    }


def test_per_day_of_empty_hours() -> None:
    assert Hours([]).per_day() == {}
    assert Hours([]).per_day(fill_gaps=False) == {}


def test_per_ticket(hours: Hours) -> None:
    assert hours.per_ticket() == {"OTHER-4": 8.0, "TICKET-1": 13.0}


def test_per_ticket_of_empty_hours() -> None:
    assert Hours([]).per_ticket() == {}


def test_per_project(hours: Hours) -> None:
    assert hours.per_project() == {"OTHER": 8.0, "TICKET": 13.0}


def test_per_project_of_empty_hours() -> None:
    assert Hours([]).per_project() == {}
