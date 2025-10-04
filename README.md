# README

An overengineered python script to move hours from CSV to Jira.

## Usage Instructions

### Requirements

* Python 3.13
* Poetry

### Installation

First, set up project dependencies:

    poetry install

### Running the Application

View all available options and arguments:

    poetry run jirahours --help

To validate the CSV file without submitting:

    poetry run jirahours check path/to/the_csv_file.csv

To submit hours from the CSV file:

    poetry run jirahours submit path/to/the_csv_file.csv

The application will prompt for:
* host, e.g. `example.atlassian.net`
* username, e.g. `myemail@example.com`
* api-key, e.g. `random_letters`

Alternatively, parameters can be given as env variables:

    JH_HOST=example.atlassian.net \
    JH_USERNAME=my.email@example.com \
    JH_API_KEY=something \
    poetry run jirahours path/to/hours.csv

### CSV Format Specification

CSV format rules:
* `;` is used as csv delimiter
* Double quote `"` used as csv quote character
* Row with all cells empty are skipped

Columns
* Column 1: Date, e.g. `25.01.2024`
* Column 2: Hours, e.g. `2,5` means two and a half hours
* Column 3: Jira ticket, e.g. `TICKET-123`
* Column 4: Description, e.g. `Did something`

## Development

### Running Unit Tests

Execute unit tests with coverage:

    poetry run pytest --cov=jirahours

### Source Code Quality

Format source code with black

    poetry run black src tests

Format source code imports with isort

    poetry run isort src tests

Check type declarations with mypy

    poetry run mypy

### Dependency Management

Python version and dependencies are managed in `pyproject.toml`.

Regenerate lock file

    poetry lock

View dependency tree

    poetry show --tree

Check outdated dependencies

    poetry show --outdated
