# README

I over-engineered a python script to move hours from CSV to Jira.


# How to run

Requirements
* Python 3.12
* Poetry

First setup things

    poetry install

This describes options and arguments

    poetry run jirahours --help

Basic usage is

    poetry run jirahours path/to/the_csv_file.csv

Software will ask
* host, e.g. `example.atlassian.net`
* username, e.g. `myemail@example.com`
* api-key, e.g. `random_letters`

Alternatively parameters can be given as env variables

    JH_HOST=example.atlassian.net \
    JH_USERNAME=my.email@example.com \
    JH_API_KEY=something \
    poetry run jirahours path/to/hours.csv


# CSV Format

CSV format rules:
* `;` is used as csv delimiter
* Double quote `"` used as csv quote character
* Row with all cells empty are skipped

Columns
* Column 1: Date, e.g. `25.01.2024`
* Column 2: Hours, e.g. `2,5` means two and a half hours
* Column 3: Jira ticket, e.g. `TICKET-123`
* Column 4: Description, e.g. `Did something`


## Code quality

Format source code with black

    poetry run black src tests

Format source code imports with isort

    poetry run isort src tests

Check type declarations with mypy

    poetry run mypy src tests

Check unit tests with pytest

    poetry run pytest --cov=jirahours
