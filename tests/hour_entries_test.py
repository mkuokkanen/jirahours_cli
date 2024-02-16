from datetime import date

import pytest

from jirahours.hour_entries import HourEntries
from jirahours.hour_entry import HourEntry


@pytest.fixture
def entry_1() -> HourEntry:
    return HourEntry(1, "1.1.2020", "6", "TICKET-1", "Description A")


@pytest.fixture
def entry_2() -> HourEntry:
    return HourEntry(2, "1.1.2020", "7", "TICKET-1", "Description B")


@pytest.fixture
def entry_3() -> HourEntry:
    return HourEntry(3, "", "", "", "")


@pytest.fixture
def entry_4() -> HourEntry:
    return HourEntry(4, "3.1.2020", "8", "TICKET-4", "Description D")


@pytest.fixture()
def hour_entries(
    entry_1: HourEntry, entry_2: HourEntry, entry_3: HourEntry, entry_4: HourEntry
) -> HourEntries:
    hour_entries = HourEntries()
    hour_entries.add_entry(entry_1)
    hour_entries.add_entry(entry_2)
    hour_entries.add_entry(entry_3)
    hour_entries.add_entry(entry_4)
    return hour_entries


def test_entries(hour_entries: HourEntries) -> None:
    assert len(hour_entries.entries) == 4


def test_valid_entries(hour_entries: HourEntries) -> None:
    assert len(hour_entries.valid_entries) == 3


def test_min_date(hour_entries: HourEntries) -> None:
    assert hour_entries.min_date() == date(2020, 1, 1)


def test_max_date(hour_entries: HourEntries) -> None:
    assert hour_entries.max_date() == date(2020, 1, 3)


def test_hours_per_date(hour_entries: HourEntries) -> None:
    assert hour_entries.hours_per_date(date(2020, 1, 1)) == 13
    assert hour_entries.hours_per_date(date(2020, 1, 2)) == 0
    assert hour_entries.hours_per_date(date(2020, 1, 3)) == 8
    assert hour_entries.hours_per_date(date(2020, 1, 4)) == 0


def test_tickets(hour_entries: HourEntries) -> None:
    assert hour_entries.tickets() == ["TICKET-1", "TICKET-4"]


@pytest.mark.parametrize(
    "ticket, expected_hours",
    [
        ("TICKET-1", 13),
        ("TICKET-2", 0),
        ("TICKET-3", 0),
        ("TICKET-4", 8),
    ],
)
def test_hours_per_ticket(
    hour_entries: HourEntries, ticket: str, expected_hours: int
) -> None:
    assert hour_entries.hours_per_ticket(ticket) == expected_hours
