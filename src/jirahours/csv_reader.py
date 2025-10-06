import csv
from pathlib import Path

from jirahours.exceptions import CsvError
from jirahours.model import Entry, Hours, Row


def csv_file_to_hours(path: Path) -> Hours:
    entries = _csv_file_to_entries(path)
    return Hours(entries)


def _csv_file_to_entries(path: Path) -> list[Entry]:
    rows = _csv_file_to_rows(path)
    entries = [Entry(row) for row in rows]
    return entries


def _csv_file_to_rows(path: Path) -> list[Row]:
    rows: list[Row] = []
    with path.open(mode="r", encoding="utf-8-sig") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";", quotechar='"')
        line_counter = 0
        for row in csv_reader:
            line_counter += 1
            # Checks
            _check_column_count(line_counter, row)
            _check_all_filled_or_empty(line_counter, row)
            # To object
            ro = _row_to_object(line_counter, row)
            rows.append(ro)
    return rows


def _check_column_count(line: int, row: list[str]) -> None:
    """Check column count is 4"""
    columns = len(row)
    if not columns == 4:
        raise CsvError(line, f"found {columns} columns instead of expected 4")


def _check_all_filled_or_empty(line: int, row: list[str]) -> None:
    """Check that row is fully empty or fully filled"""
    all_empty = all(r.strip() == "" for r in row)
    all_filled = all(r.strip() != "" for r in row)
    if not (all_empty or all_filled):
        raise CsvError(line, f"row only partly filled")


def _row_to_object(line_counter: int, row: list[str]) -> Row:
    return Row(
        line=line_counter,
        date_cell=row[0],
        hours_cell=row[1],
        ticket_cell=row[2],
        description_cell=row[3],
    )
