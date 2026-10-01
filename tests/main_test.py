from click.testing import CliRunner

from jirahours.main import cli


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
