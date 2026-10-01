"""StdlibTimesheet itself: how it reads the file."""

from pathlib import Path
from typing import Any

import pytest

from jirahours.timesheet import TimesheetError
from jirahours.timesheet.implementations import StdlibTimesheet


def test_file_is_read_lazily() -> None:
    """Constructing must not touch the file; the first question reads it."""
    sheet = StdlibTimesheet(Path("tests/csv_files/does_not_exist.csv"))
    with pytest.raises(FileNotFoundError):
        sheet.worklogs()


def test_file_is_read_only_once() -> None:
    sheet = StdlibTimesheet(Path("tests/csv_files/ok.csv"))
    assert sheet._hours is sheet._hours


def test_delimiter_and_quotechar_are_configurable(tmp_path: Path) -> None:
    csv_file = tmp_path / "comma.csv"
    csv_file.write_text("1.1.2020,6,ABC-1,Work\n", encoding="utf-8")
    sheet = StdlibTimesheet(csv_file, delimiter=",")
    assert [w.ticket for w in sheet.worklogs()] == ["ABC-1"]


def test_file_is_closed_even_when_validation_rejects_a_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Parsing must finish inside the with block, or the handle outlives it.

    The raised error is deliberately kept alive while the handles are checked:
    its traceback holds the frames that would keep an abandoned lazy reader,
    and with it the open file, from being collected. Letting the error go out
    of scope first hides the very leak this is guarding against.
    """
    opened = []
    real_open = Path.open

    def tracking_open(self: Path, *args: Any, **kwargs: Any) -> Any:
        handle = real_open(self, *args, **kwargs)
        opened.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", tracking_open)

    sheet = StdlibTimesheet(Path("tests/csv_files/error_extra_column.csv"))
    with pytest.raises(TimesheetError) as exc_info:
        sheet.worklogs()

    assert exc_info.value.line == 2
    assert opened, "the file was never opened"
    assert all(handle.closed for handle in opened), "the file was left open"
