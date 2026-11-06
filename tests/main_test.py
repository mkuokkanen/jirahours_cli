import pytest
from click import ClickException
from click.testing import CliRunner

from jirahours.main import _send_worklogs, cli
from jirahours.submitter.base import Submitted, Submitter
from jirahours.timesheet.base import Worklog


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output


def test_check_reports_a_rejected_file_without_a_stray_blank_line() -> None:
    """The error follows the 'Reading' line directly, as it always has."""
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "tests/csv_files/error_extra_column.csv"])
    assert result.exit_code == 1
    assert result.output == (
        "\n"
        "Reading csv file 'tests/csv_files/error_extra_column.csv'\n"
        "Error: csv line 2: found 5 columns instead of expected 4\n"
    )


def test_check_accepts_a_good_file() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "tests/csv_files/ok.csv"])
    assert result.exit_code == 0
    assert "Hours per project" in result.output


class FakeSubmitter(Submitter):
    def __init__(self, failing_lines: frozenset[int] = frozenset()) -> None:
        self.sent: list[Worklog] = []
        self._failing_lines = failing_lines

    def add_worklog(self, worklog: Worklog) -> Submitted:
        self.sent.append(worklog)
        if worklog.line in self._failing_lines:
            return Submitted(line=worklog.line, ok=False, message="404, fake, no")
        return Submitted(line=worklog.line, ok=True, message="201, fake, ok")


WORKLOGS = [
    Worklog(line=2, started="s1", seconds=3600, ticket="ABC-1", description="a"),
    Worklog(line=4, started="s2", seconds=1800, ticket="ABC-2", description="b"),
    Worklog(line=5, started="s3", seconds=900, ticket="ABC-3", description="c"),
]


def test_send_worklogs_stops_on_failure_and_tells_what_was_sent(
    capsys: pytest.CaptureFixture[str],
) -> None:
    submitter = FakeSubmitter(failing_lines=frozenset({4}))
    with pytest.raises(ClickException) as error:
        _send_worklogs(WORKLOGS, submitter)
    assert submitter.sent == WORKLOGS[:2]
    assert capsys.readouterr().out == (
        "2: Sending line \n"
        "2: 201, fake, ok\n"
        "4: Sending line \n"
        "4: 404, fake, no\n"
    )
    assert error.value.message == (
        "Line 4 failed. "
        "Lines sent: 2. "
        "Remove the sent lines from the file before running again, "
        "or they will be sent twice."
    )


def test_send_worklogs_says_when_nothing_was_sent() -> None:
    with pytest.raises(ClickException, match="Lines sent: none"):
        _send_worklogs(WORKLOGS, FakeSubmitter(failing_lines=frozenset({2})))
