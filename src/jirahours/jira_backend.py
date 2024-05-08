import httpx
from httpx import Response

from jirahours.model import Entry


class JiraBackend:
    def __init__(self, host: str, username: str, api_key: str):
        self._host = host
        self._client = httpx.Client(auth=httpx.BasicAuth(username, api_key))

    def add_worklog_to_ticket(self, hour_entry: Entry) -> Response:
        url = f"https://{self._host}/rest/api/3/issue/{hour_entry.ticket}/worklog"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        params = {"notifyUsers": False}
        data = self.build_body(hour_entry)
        r = self._client.post(url, json=data, params=params, headers=headers)
        return r

    @staticmethod
    def build_body(hour_entry: Entry) -> object:
        return {
            "comment": {
                "content": [
                    {
                        "content": [
                            {
                                "text": hour_entry.description,
                                "type": "text",
                            }
                        ],
                        "type": "paragraph",
                    }
                ],
                "type": "doc",
                "version": 1,
            },
            "started": hour_entry.started,
            "timeSpentSeconds": hour_entry.seconds,
        }
