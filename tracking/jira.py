import dataclasses
from datetime import datetime
from typing import Callable
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from aiohttp import ClientSession

from tracking.values import SavedWorklogValue, WorklogValue

# 2022-04-29T11:30:00.000+0000'

"""
'comment': 'Sync with Stan',
'started': '2022-04-29T11:30:00.000+0000',
'timeSpentSeconds': 3600,
"""


@dataclasses.dataclass
class JiraClient:
    session: ClientSession
    now: Callable[[], datetime]
    jira_base_url: str = "https://jira.clutch.co/rest/api/2/"

    async def create(self, worklog: WorklogValue) -> SavedWorklogValue:
        url = urljoin(self.jira_base_url, f"issue/{worklog.issue}/worklog")
        data = {
            "started": worklog.started_at.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "timeSpentSeconds": worklog.spent.seconds,
            "comment": worklog.comment,
        }
        async with self.session.post(url, json=data) as response:
            response.raise_for_status()
            data = await response.json()

        return SavedWorklogValue(id=data["id"], created_at=self.now(), worklog=worklog)

    async def delete(self, saved_worklog: SavedWorklogValue) -> SavedWorklogValue:
        url = urljoin(
            self.jira_base_url,
            f"issue/{saved_worklog.worklog.issue}/worklog/{saved_worklog.id}",
        )

        async with self.session.delete(url) as response:
            response.raise_for_status()

        return saved_worklog
