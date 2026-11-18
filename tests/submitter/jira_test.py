import json

import httpx2

from jirahours.submitter.jira import JiraSubmitter
from jirahours.timesheet.base import Worklog

WORKLOG = Worklog(
    line=3,
    started="2026-10-01T09:00:00.000+0300",
    seconds=5400,
    ticket="ABC-1",
    description="Code review",
)


def _submitter(
    response: httpx2.Response, requests: list[httpx2.Request]
) -> JiraSubmitter:
    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return response

    transport = httpx2.MockTransport(handler)
    return JiraSubmitter("example.atlassian.net", "me", "key", transport=transport)


def test_add_worklog_posts_to_the_tickets_worklog() -> None:
    requests: list[httpx2.Request] = []
    _submitter(httpx2.Response(201, text="created"), requests).add_worklog(WORKLOG)
    [request] = requests
    assert request.method == "POST"
    assert str(request.url) == (
        "https://example.atlassian.net/rest/api/3/issue/ABC-1/worklog"
        "?notifyUsers=false"
    )
    assert json.loads(request.content) == {
        "comment": {
            "content": [
                {
                    "content": [{"text": "Code review", "type": "text"}],
                    "type": "paragraph",
                }
            ],
            "type": "doc",
            "version": 1,
        },
        "started": "2026-10-01T09:00:00.000+0300",
        "timeSpentSeconds": 5400,
    }


def test_add_worklog_reports_a_rejection_as_failed() -> None:
    submitted = _submitter(httpx2.Response(404, text="no such issue"), []).add_worklog(
        WORKLOG
    )
    assert submitted.line == 3
    assert not submitted.ok
    assert submitted.message.startswith("404, ")
    assert submitted.message.endswith("no such issue")


def test_add_worklog_reports_a_network_error_as_failed() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ReadTimeout("timed out", request=request)

    submitter = JiraSubmitter(
        "example.atlassian.net", "me", "key", transport=httpx2.MockTransport(handler)
    )
    submitted = submitter.add_worklog(WORKLOG)
    assert submitted.line == 3
    assert not submitted.ok
    assert submitted.message == (
        "network error, the worklog may or may not be saved: timed out"
    )
