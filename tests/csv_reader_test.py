from pathlib import Path

import pytest

from jirahours.csv_reader import read_csv
from jirahours.errors import CsvError
from jirahours.hour_entries import HourEntries


@pytest.fixture
def he() -> HourEntries:
    return HourEntries()


def test_ok_csv(he: HourEntries) -> None:
    read_csv(Path("tests/csv_files/ok.csv"), he)
    data = he.entries
    # checks
    assert len(data) == 3
    # row with quotes
    assert data[0].line == 1
    assert data[0].date_cell == "02.01.2024"
    assert data[0].hours_cell == "2,5"
    assert data[0].ticket_cell == "TICKET-123"
    assert data[0].description_cell == "Some description, with comma"
    # empty row
    assert data[1].line == 2
    assert data[1].date_cell == ""
    assert data[1].hours_cell == ""
    assert data[1].ticket_cell == ""
    assert data[1].description_cell == ""
    # row without quotes
    assert data[2].line == 3
    assert data[2].date_cell == "13.1.2024"
    assert data[2].hours_cell == "8"
    assert data[2].ticket_cell == "TICKET-321"
    assert data[2].description_cell == "Other description with emoji without quotes 👍"


def test_ok_bom_csv(he: HourEntries) -> None:
    read_csv(Path("tests/csv_files/ok_bom.csv"), he)
    data = he.entries
    assert len(data) == 1
    assert data[0].line == 1
    assert data[0].date_cell == "5.1.2024"
    assert data[0].hours_cell == "2,5"
    assert data[0].ticket_cell == "TICKET-123"
    assert data[0].description_cell == "File starts with BOM character"


def test_csv_file_extra_column(he: HourEntries) -> None:
    with pytest.raises(CsvError) as exc_info:
        read_csv(Path("tests/csv_files/error_extra_column.csv"), he)
    assert str(exc_info.value) == "csv line 2: found 5 columns instead of expected 4"


def test_csv_partly_filled(he: HourEntries) -> None:
    with pytest.raises(CsvError) as exc_info:
        read_csv(Path("tests/csv_files/error_partly_filled.csv"), he)
    assert str(exc_info.value) == "csv line 1: row only partly filled"
