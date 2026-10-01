"""One subpackage per implementation, each free to be structured its own way."""

from jirahours.timesheet.implementations.stdlib import StdlibTimesheet

__all__ = ["StdlibTimesheet"]
