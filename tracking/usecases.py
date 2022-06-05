import asyncio
import dataclasses
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from tracking.jira import JiraClient
from tracking.saved_worklog_repository import SavedWorklogRepository
from tracking.worklog_repository import WorklogRepository


@dataclasses.dataclass
class SyncWorklogsUsecase:
    saved_worklog_repository: SavedWorklogRepository
    worklog_repository: WorklogRepository
    jira_client: JiraClient
    timezone: ZoneInfo

    async def run(self, track_path: Path) -> None:
        worklogs = await self.worklog_repository.read(track_path)

        if not worklogs:
            return

        day_start = datetime.combine(worklogs[0].started_at.date(), time.min, tzinfo=self.timezone)
        day_end = datetime.combine(day_start.date(), time.max, tzinfo=self.timezone)

        saved_worklogs = await self.saved_worklog_repository.list(day_start, day_end)

        if set(map(lambda saved_worklog: saved_worklog.worklog, saved_worklogs)) != set(worklogs):
            deleted_saved_worklogs = await asyncio.gather(
                *map(self.jira_client.delete, saved_worklogs),
                return_exceptions=True,
            )
            for deleted_saved_worklog in deleted_saved_worklogs:
                if isinstance(deleted_saved_worklog, Exception):
                    continue

                await self.saved_worklog_repository.delete(deleted_saved_worklog)

        saved_worklogs = await asyncio.gather(*map(self.jira_client.create, worklogs), return_exceptions=True)

        for saved_worklog in saved_worklogs:
            await self.saved_worklog_repository.write(saved_worklog)

        await self.saved_worklog_repository.connection.commit()
