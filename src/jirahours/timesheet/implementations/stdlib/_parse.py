"""This implementation's take on validating the CSV shape.

Row by row, with plain Python checks, which is what the standard library's
csv.reader naturally gives you. Another implementation is free to express the
same rules however its library prefers.
"""

from collections.abc import Iterable

from jirahours.timesheet.implementations.stdlib._errors import CsvError
from jirahours.timesheet.implementations.stdlib._model import Entry, Hours, Row

EXPECTED_COLUMNS = 4


def to_hours(cells: Iterable[list[str]]) -> Hours:
    """Validate every row and interpret it, or raise on the first bad one."""
    entries: list[Entry] = []
    for line, row in enumerate(cells, start=1):
        _check_column_count(line, row)
        _check_all_filled_or_empty(line, row)
        entries.append(Entry(_to_row(line, row)))
    return Hours(entries)


def _check_column_count(line: int, cells: list[str]) -> None:
    """Check column count is 4"""
    columns = len(cells)
    if not columns == EXPECTED_COLUMNS:
        raise CsvError(
            line, f"found {columns} columns instead of expected {EXPECTED_COLUMNS}"
        )


def _check_all_filled_or_empty(line: int, cells: list[str]) -> None:
    """Check that row is fully empty or fully filled"""
    all_empty = all(c.strip() == "" for c in cells)
    all_filled = all(c.strip() != "" for c in cells)
    if not (all_empty or all_filled):
        raise CsvError(line, "row only partly filled")


def _to_row(line: int, cells: list[str]) -> Row:
    return Row(
        line=line,
        date_cell=cells[0],
        hours_cell=cells[1],
        ticket_cell=cells[2],
        description_cell=cells[3],
    )
