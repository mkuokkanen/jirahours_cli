import pytest

from jirahours.exceptions import CsvError
from jirahours.model import Entry, Row


def create_entry(
    line: int = 3,
    date_cell: str = "13.2.2024",
    hours_cell: str = "5",
    ticket_cell: str = "TICKET-321",
    description_cell: str = "Description about something",
) -> Entry:
    row = Row(
        line=line,
        date_cell=date_cell,
        hours_cell=hours_cell,
        ticket_cell=ticket_cell,
        description_cell=description_cell,
    )
    return Entry(row)


def test_all_fields_ok() -> None:
    h = create_entry()
    assert h.line == 3
    assert h.started == "2024-02-13T03:00:00.000+0000"
    assert h.seconds == 5 * 60 * 60
    assert h.ticket == "TICKET-321"
    assert h.description == "Description about something"


def test_date_not_of_supported_format() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_entry(date_cell="2024-01-01")
    assert (
        str(exc_info.value)
        == "csv line 3: time data '2024-01-01' does not match format '%d.%m.%Y'"
    )


def test_hours() -> None:
    h = create_entry(hours_cell="0,5")
    assert h.seconds == 30 * 60

    h = create_entry(hours_cell="0,9")
    assert h.seconds == 54 * 60

    h = create_entry(hours_cell="12")
    assert h.seconds == 12 * 60 * 60


def test_hours_not_a_number() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_entry(hours_cell="Text in wrong cell")
    assert (
        str(exc_info.value)
        == "csv line 3: could not convert string to float: 'Text in wrong cell'"
    )


def test_hours_too_small() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_entry(hours_cell="0,4")
    assert str(exc_info.value) == "csv line 3: hour value '0,4' is less than 30 minutes"


def test_hours_too_big() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_entry(hours_cell="13")
    assert str(exc_info.value) == "csv line 3: hour value '13' is more than 12 hours"


def test_ticket_wrong_format() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_entry(ticket_cell="123-ABC")
    assert (
        str(exc_info.value)
        == "csv line 3: ticket value '123-ABC' is not in correct format"
    )


def test_description_missing() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_entry(description_cell="    ")
    assert str(exc_info.value) == "csv line 3: description is missing"
