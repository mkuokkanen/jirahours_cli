from datetime import datetime, timedelta

import pytest

from jirahours.errors import CsvError
from jirahours.hour_entry import HourEntry


def create_hour_entry(
    line: int = 3,
    date_cell: str = datetime.today().strftime("%d.%m.%Y"),
    hours_cell: str = "5",
    ticket_cell: str = "TICKET-321",
    description_cell: str = "Description about something",
) -> HourEntry:
    return HourEntry(
        line=line,
        date_cell=date_cell,
        hours_cell=hours_cell,
        ticket_cell=ticket_cell,
        description_cell=description_cell,
    )


def test_all_fields_ok() -> None:
    h = create_hour_entry()
    assert h.line == 3
    assert h.started == datetime.today().strftime("%Y-%m-%d") + "T03:00:00.000+0000"
    assert h.seconds == 5 * 60 * 60
    assert h.ticket == "TICKET-321"
    assert h.description == "Description about something"


def test_date_not_of_supported_format() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(date_cell="2024-01-01")
    assert (
        str(exc_info.value)
        == "csv line 3: time data '2024-01-01' does not match format '%d.%m.%Y'"
    )


def test_date_not_too_old() -> None:
    old_date = datetime.today() - timedelta(days=59)
    old_date_str = old_date.strftime("%d.%m.%Y")
    iso_old_date_str = old_date.strftime("%Y-%m-%d")
    h = create_hour_entry(date_cell=old_date_str)
    assert h.started == iso_old_date_str + "T03:00:00.000+0000"


def test_date_too_old() -> None:
    old_date = datetime.today() - timedelta(days=61)
    old_date_str = old_date.strftime("%d.%m.%Y")
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(date_cell=old_date_str)
    assert (
        str(exc_info.value)
        == f"csv line 3: date value '{old_date_str}' is more than 60 days old"
    )


def test_date_in_future() -> None:
    tomorrow = datetime.today() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%d.%m.%Y")
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(date_cell=tomorrow_str)
    assert (
        str(exc_info.value) == f"csv line 3: date value '{tomorrow_str}' is in future"
    )


def test_hours() -> None:
    h = create_hour_entry(hours_cell="0,5")
    assert h.seconds == 30 * 60

    h = create_hour_entry(hours_cell="0,9")
    assert h.seconds == 54 * 60

    h = create_hour_entry(hours_cell="12")
    assert h.seconds == 12 * 60 * 60


def test_hours_not_a_number() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(hours_cell="Text in wrong cell")
    assert (
        str(exc_info.value)
        == "csv line 3: could not convert string to float: 'Text in wrong cell'"
    )


def test_hours_too_small() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(hours_cell="0,4")
    assert str(exc_info.value) == "csv line 3: hour value '0,4' is less than 30 minutes"


def test_hours_too_big() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(hours_cell="13")
    assert str(exc_info.value) == "csv line 3: hour value '13' is more than 12 hours"


def test_ticket_wrong_format() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(ticket_cell="123-ABC")
    assert (
        str(exc_info.value)
        == "csv line 3: ticket value '123-ABC' is not in correct format"
    )


def test_description_missing() -> None:
    with pytest.raises(CsvError) as exc_info:
        _ = create_hour_entry(description_cell="    ")
    assert str(exc_info.value) == "csv line 3: description is missing"
