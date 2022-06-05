import dataclasses
import os
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import aiofiles
import yaml
from pytimeparse import parse

from tracking.values import WorklogValue


@dataclasses.dataclass
class WorklogRepository:
    timezone: ZoneInfo

    async def read(self, worklog_path: Path) -> list[WorklogValue]:
        async with aiofiles.open(worklog_path, "r") as file:
            content = await file.read()

        track_dict = yaml.load(content, Loader=yaml.CLoader)

        date_string = os.path.basename(worklog_path).replace(".yml", "")

        start_date = datetime.strptime(date_string, "%d-%m-%Y").date()
        start_time = time.fromisoformat(track_dict["start"])

        start_datetime = datetime.combine(start_date, start_time, tzinfo=self.timezone)

        return self._parse_worklogs(start_datetime, track_dict["worklogs"])

    def _parse_worklogs(self, start_datetime: datetime, worklog_dicts: list[dict[str, Any]]) -> list[WorklogValue]:
        worklogs: list[WorklogValue] = []

        offset = timedelta()

        for worklog_dict in worklog_dicts:
            spent = timedelta(seconds=parse(worklog_dict["spent"]))

            worklogs.append(
                WorklogValue(
                    issue=worklog_dict["issue"],
                    started_at=start_datetime + offset,
                    spent=spent,
                    comment=worklog_dict["comment"],
                ),
            )

            offset += spent

        return worklogs
