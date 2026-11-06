import httpx2

from jirahours.submitter.base import Submitted, Submitter
from jirahours.timesheet.base import Worklog


class JiraSubmitter(Submitter):
    def __init__(
        self,
        host: str,
        username: str,
        api_key: str,
        transport: httpx2.BaseTransport | None = None,
    ):
        """transport replaces the network, so tests can answer for Jira."""
        self._host = host
        self._client = httpx2.Client(
            auth=httpx2.BasicAuth(username, api_key), transport=transport
        )

    def close(self) -> None:
        self._client.close()

    def add_worklog(self, worklog: Worklog) -> Submitted:
        url = f"https://{self._host}/rest/api/3/issue/{worklog.ticket}/worklog"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        params = {"notifyUsers": False}
        data = self._build_body(worklog)
        try:
            r = self._client.post(url, json=data, params=params, headers=headers)
        except httpx2.HTTPError as e:
            # A timeout can come after Jira has already saved the worklog
            return Submitted(
                line=worklog.line,
                ok=False,
                message=f"network error, the worklog may or may not be saved: {e}",
            )
        return Submitted(
            line=worklog.line,
            ok=r.is_success,
            message=f"{r.status_code}, {r.url}, {r.text}",
        )

    @staticmethod
    def _build_body(worklog: Worklog) -> dict[str, object]:
        return {
            "comment": {
                "content": [
                    {
                        "content": [
                            {
                                "text": worklog.description,
                                "type": "text",
                            }
                        ],
                        "type": "paragraph",
                    }
                ],
                "type": "doc",
                "version": 1,
            },
            "started": worklog.started,
            "timeSpentSeconds": worklog.seconds,
        }
