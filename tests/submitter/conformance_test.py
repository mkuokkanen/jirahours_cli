"""The shared specification every Submitter implementation is held to.

Add an implementation to IMPLEMENTATIONS and either it agrees here or it fails.
Each factory builds a submitter that accepts everything it is sent, without the
network.

Deliberately loose about wording: what a submitter says about each worklog is
its own business. What is pinned is that a worklog gets a result for its own
line, and that there is something to show the user.
"""

from collections.abc import Callable

import httpx2
import pytest

from jirahours.submitter.base import Submitter
from jirahours.submitter.jira import JiraSubmitter
from jirahours.timesheet.base import Worklog

SubmitterFactory = Callable[[], Submitter]


def _jira_accepting_everything() -> Submitter:
    transport = httpx2.MockTransport(lambda request: httpx2.Response(201, json={}))
    return JiraSubmitter("example.atlassian.net", "me", "key", transport=transport)


IMPLEMENTATIONS: list[SubmitterFactory] = [
    _jira_accepting_everything,
]

WORKLOGS = [
    Worklog(line=1, started="s1", seconds=3600, ticket="ABC-1", description="a"),
    Worklog(line=3, started="s2", seconds=1800, ticket="ABC-2", description="b"),
]


@pytest.fixture(params=IMPLEMENTATIONS)
def implementation(request: pytest.FixtureRequest) -> SubmitterFactory:
    factory: SubmitterFactory = request.param
    return factory


def test_add_worklog_reports_on_the_worklogs_own_line(
    implementation: SubmitterFactory,
) -> None:
    submitted = implementation().add_worklog(WORKLOGS[1])
    assert submitted.line == 3
    assert submitted.ok
    assert submitted.message
