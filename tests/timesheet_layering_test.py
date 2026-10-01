"""The contract package must not depend on its implementations."""

import subprocess
import sys


def test_contract_does_not_import_its_implementations() -> None:
    """Importing jirahours.timesheet must not pull in any implementation.

    Checked in a fresh interpreter, because the rest of the test suite imports
    the implementations itself and would leave them in sys.modules.
    """
    code = (
        "import sys, jirahours.timesheet; "
        "print([m for m in sys.modules if 'timesheet.implementations' in m])"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "[]"


def test_implementations_are_reachable_on_their_own() -> None:
    """Importing only the implementations package is enough to get a Timesheet."""
    code = (
        "from jirahours.timesheet import Timesheet; "
        "from jirahours.timesheet.implementations import StdlibTimesheet; "
        "print(issubclass(StdlibTimesheet, Timesheet))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "True"
