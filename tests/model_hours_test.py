from datetime import date

import pytest

from jirahours.model import Entry, Hours, Row


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
    return Entry(Row(4, "3.1.2020", "8", "TICKET-4", "Description D"))


@pytest.fixture()
def hours(entry_1: Entry, entry_2: Entry, entry_3: Entry, entry_4: Entry) -> Hours:
    entries = [entry_1, entry_2, entry_3, entry_4]
    hour_entries = Hours(entries)
    return hour_entries


def test_length_of_entries(hours: Hours) -> None:
    assert len(hours.entries) == 4


def test_length_of_valid_entries(hours: Hours) -> None:
    assert len(hours.valid_entries) == 3


def test_min_date(hours: Hours) -> None:
    assert hours.min_date() == date(2020, 1, 1)


def test_max_date(hours: Hours) -> None:
    assert hours.max_date() == date(2020, 1, 3)


def test_hours_per_date(hours: Hours) -> None:
    assert hours.hours_per_date(date(2020, 1, 1)) == 13
    assert hours.hours_per_date(date(2020, 1, 2)) == 0
    assert hours.hours_per_date(date(2020, 1, 3)) == 8
    assert hours.hours_per_date(date(2020, 1, 4)) == 0


def test_tickets(hours: Hours) -> None:
    assert hours.tickets() == ["TICKET-1", "TICKET-4"]


@pytest.mark.parametrize(
    "ticket, expected_hours",
    [
        ("TICKET-1", 13),
        ("TICKET-2", 0),
        ("TICKET-3", 0),
        ("TICKET-4", 8),
    ],
)
def test_hours_per_ticket(hours: Hours, ticket: str, expected_hours: int) -> None:
    assert hours.hours_per_ticket(ticket) == expected_hours
