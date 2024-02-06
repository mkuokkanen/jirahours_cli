import csv
from pathlib import Path

from jirahours.errors import CsvError
from jirahours.hour_entry import HourEntry


def read_csv(path: Path) -> list[HourEntry]:
    csv_entries = []
    with path.open(mode="r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";", quotechar='"')
        line_counter = 0
        for row in csv_reader:
            line_counter += 1
            # Checks
            check_column_count(line_counter, row)
            check_all_filled_or_empty(line_counter, row)
            # To object
            ro = row_to_object(line_counter, row)
            csv_entries.append(ro)
    return csv_entries


def check_column_count(line: int, row: list[str]) -> None:
    """Check column count is 4"""
    columns = len(row)
    if not columns == 4:
        raise CsvError(line, f"found {columns} columns instead of expected 4")


def check_all_filled_or_empty(line: int, row: list[str]) -> None:
    """Check that row is fully empty or fully filled"""
    all_empty = all(r.strip() == "" for r in row)
    all_filled = all(r.strip() != "" for r in row)
    if not (all_empty or all_filled):
        raise CsvError(line, f"row only partly filled")


def row_to_object(line_counter: int, row: list[str]) -> HourEntry:
    return HourEntry(
        line=line_counter,
        date_cell=row[0],
        hours_cell=row[1],
        ticket_cell=row[2],
        description_cell=row[3],
    )
