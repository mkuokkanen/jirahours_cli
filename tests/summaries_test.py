import pytest

from jirahours.hour_entries import HourEntries, HourEntry
from jirahours.summaries import hours_per_day, hours_per_ticket, rows


@pytest.fixture
def sample_hour_entry_1():
    return HourEntry(
        ticket_cell="JKL-123",
        description_cell="Sample Issue",
        hours_cell="1",
        date_cell="01.05.2024",
        line=1,
    )


@pytest.fixture
def sample_hour_entry_2():
    return HourEntry(
        ticket_cell="ABC-456",
        description_cell="Another Issue",
        hours_cell="2",
        date_cell="03.05.2024",
        line=2,
    )


@pytest.fixture
def sample_hour_entry_3():
    return HourEntry(
        ticket_cell="ABC-456",
        description_cell="Another Issue",
        hours_cell="2",
        date_cell="04.05.2024",
        line=3,
    )


#
# ROWS
#


def test_rows_empty_data():
    empty_data = HourEntries()
    assert rows(empty_data) == "Data from csv file"


def test_rows_with_single_entry_data(sample_hour_entry_1):
    data = HourEntries()
    data.add_entry(sample_hour_entry_1)
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000 (01.05.2024), 3600 (1), 'JKL-123', 'Sample Issue'
    """.strip()
    assert rows(data) == expected_output


def test_rows_with_multiple_entries_data(
    sample_hour_entry_1, sample_hour_entry_2, sample_hour_entry_3
):
    data = HourEntries()
    data.add_entry(sample_hour_entry_1)
    data.add_entry(sample_hour_entry_2)
    data.add_entry(sample_hour_entry_3)
    expected_output = """
Data from csv file
1: 2024-05-01T02:00:00.000+0000 (01.05.2024), 3600 (1), 'JKL-123', 'Sample Issue'
2: 2024-05-03T02:00:00.000+0000 (03.05.2024), 7200 (2), 'ABC-456', 'Another Issue'
3: 2024-05-04T02:00:00.000+0000 (04.05.2024), 7200 (2), 'ABC-456', 'Another Issue'
    """.strip()
    assert rows(data) == expected_output


#
# HOURS_PER_DAY
#


def test_hours_per_day_empty_data():
    empty_data = HourEntries()
    assert hours_per_day(empty_data) == "Hours per date"


def test_hours_per_day_with_single_entry_data(sample_hour_entry_1):
    data = HourEntries()
    data.add_entry(sample_hour_entry_1)
    expected_output = """
Hours per date
2024-05-01: 1.0
    """.strip()
    assert hours_per_day(data) == expected_output


def test_hours_per_day_with_multiple_entries_data(
    sample_hour_entry_1, sample_hour_entry_2, sample_hour_entry_3
):
    data = HourEntries()
    data.add_entry(sample_hour_entry_1)
    data.add_entry(sample_hour_entry_2)
    data.add_entry(sample_hour_entry_3)
    expected_output = """
Hours per date
2024-05-01: 1.0
2024-05-02: -
2024-05-03: 2.0
2024-05-04: 2.0
    """.strip()
    assert hours_per_day(data) == expected_output


#
# HOURS_PER_TICKET
#


def test_hours_per_ticket_empty_data():
    empty_data = HourEntries()
    assert hours_per_ticket(empty_data) == "Hours per ticket"


def test_hours_per_ticket_with_single_entry_data(sample_hour_entry_1):
    data = HourEntries()
    data.add_entry(sample_hour_entry_1)
    expected_output = """
Hours per ticket
JKL-123: 1.0
    """.strip()
    assert hours_per_ticket(data) == expected_output


def test_hours_per_ticket_with_multiple_entries_data(
    sample_hour_entry_1, sample_hour_entry_2, sample_hour_entry_3
):
    data = HourEntries()
    data.add_entry(sample_hour_entry_1)
    data.add_entry(sample_hour_entry_2)
    data.add_entry(sample_hour_entry_3)
    expected_output = """
Hours per ticket
ABC-456: 4.0
JKL-123: 1.0
    """.strip()
    assert hours_per_ticket(data) == expected_output
