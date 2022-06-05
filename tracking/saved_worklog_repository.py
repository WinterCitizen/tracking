import dataclasses
import logging
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import aiosqlite

from tracking.values import SavedWorklogValue, WorklogValue

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SavedWorklogRepository:
    connection: aiosqlite.Connection
    timezone: ZoneInfo

    async def write(self, saved_worklog_value: SavedWorklogValue) -> None:
        await self.connection.execute(
            """
            INSERT INTO worklogs (id, issue, started_at, spent, comment, created_at)
            VALUES (:id, :issue, :started_at, :spent, :comment, :created_at)
            """,
            {
                "id": saved_worklog_value.id,
                "issue": saved_worklog_value.worklog.issue,
                "started_at": int(saved_worklog_value.worklog.started_at.timestamp()),
                "spent": saved_worklog_value.worklog.spent.seconds,
                "comment": saved_worklog_value.worklog.comment,
                "created_at": int(saved_worklog_value.created_at.timestamp()),
            },
        )

    async def list(self, from_started_at: datetime, to_started_at: datetime) -> list[SavedWorklogValue]:
        self.connection.row_factory = sqlite3.Row
        rows = await self.connection.execute_fetchall(
            "SELECT * FROM worklogs WHERE started_at >= :from_started_at AND started_at <= :to_started_at",
            {
                "from_started_at": int(from_started_at.timestamp()),
                "to_started_at": int(to_started_at.timestamp()),
            },
        )

        saved_worklog_values: list[SavedWorklogValue] = []

        for row in rows:
            saved_worklog_values.append(
                SavedWorklogValue(
                    id=row["id"],
                    created_at=datetime.fromtimestamp(row["created_at"], tz=ZoneInfo("UTC")).astimezone(self.timezone),
                    worklog=WorklogValue(
                        issue=row["issue"],
                        started_at=datetime.fromtimestamp(row["started_at"], tz=ZoneInfo("UTC")).astimezone(
                            self.timezone,
                        ),
                        spent=timedelta(seconds=row["spent"]),
                        comment=row["comment"],
                    ),
                )
            )

        return saved_worklog_values

    async def delete(self, saved_worklog: SavedWorklogValue) -> int:
        cursor = await self.connection.execute("DELETE FROM worklogs WHERE id = :id", {"id": saved_worklog.id})
        return cursor.rowcount
