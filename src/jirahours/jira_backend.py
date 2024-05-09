import httpx
from httpx import Response


class JiraBackend:
    def __init__(self, host: str, username: str, api_key: str):
        self._host = host
        self._client = httpx.Client(auth=httpx.BasicAuth(username, api_key))

    def add_worklog_to_ticket(
        self, ticket: str, started: str, seconds: int, description: str
    ) -> Response:
        url = f"https://{self._host}/rest/api/3/issue/{ticket}/worklog"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        params = {"notifyUsers": False}
        data = self.build_body(started, seconds, description)
        r = self._client.post(url, json=data, params=params, headers=headers)
        return r

    @staticmethod
    def build_body(started: str, seconds: int, description: str) -> object:
        return {
            "comment": {
                "content": [
                    {
                        "content": [
                            {
                                "text": description,
                                "type": "text",
                            }
                        ],
                        "type": "paragraph",
                    }
                ],
                "type": "doc",
                "version": 1,
            },
            "started": started,
            "timeSpentSeconds": seconds,
        }
